"""FastAPI app. Run with:  uvicorn api.main:app --reload   (from the mvp/ folder)."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from nordic_flow.llm import GroqClient
from nordic_flow.mapping import suggest
from . import audit, service
from .db import Database
from .service import ApiError

WEB = Path(__file__).resolve().parent.parent / "web"
DEFAULT_DB = Path(__file__).resolve().parent.parent / "var" / "app.db"


class RunRequest(BaseModel):
    mode: Literal["lp", "milp"] = "milp"
    time_limit: float = Field(30, gt=0, le=300)


class SampleRequest(BaseModel):
    name: str


class OverrideRequest(BaseModel):
    zone: str
    sku: str
    warehouse: str
    pallets: float = Field(ge=0)
    reason: str = ""
    actor: str = "planner"


class WhatIfRequest(BaseModel):
    changes: list[dict] = Field(min_length=1)
    mode: Literal["lp", "milp"] = "milp"
    time_limit: float = Field(30, gt=0, le=300)
    reference_run_id: int | None = None
    actor: str = "planner"


class ApproveExplanation(BaseModel):
    text: str | None = None
    actor: str = "planner"


class Decision(BaseModel):
    decision: Literal["approve", "reject"]
    comment: str = ""
    actor: str = "planner"


class ExplainRequest(BaseModel):
    use_llm: bool = False        # default: deterministic summary; the LLM is opt-in per request


class MappingConfirm(BaseModel):
    scenario_id: int
    external: dict
    sku_id: str
    actor: str = "planner"


class MappingRequest(BaseModel):
    scenario_id: int
    items: list[dict] = Field(min_length=1, max_length=200)
    use_llm: bool = False


def create_app(db_path: str | Path | None = None, llm_factory=None) -> FastAPI:
    db = Database(db_path or os.environ.get("NORDIC_DB") or DEFAULT_DB)
    get_llm = llm_factory or GroqClient
    app = FastAPI(title="Nordic Flow MVP", version="0.1")

    @app.exception_handler(ApiError)
    async def api_error(_: Request, e: ApiError):
        return JSONResponse(status_code=e.status, content={"code": e.code, "message": e.message, "details": e.details})

    @app.exception_handler(Exception)
    async def unexpected(_: Request, e: Exception):
        return JSONResponse(status_code=500, content={"code": "internal_error", "message": "Unexpected error.", "details": None})

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.get("/api/config")
    def config():
        c = get_llm()
        return {"llm_enabled": c.enabled, "llm_model": c.model if c.enabled else None, "samples": service.SAMPLE_NAMES}

    # ----- scenarios -----
    @app.post("/api/scenarios")
    async def upload(files: list[UploadFile] = File(...), name: str = Form("Uploaded scenario")):
        content = {}
        if len(files) == 1 and (files[0].filename or "").lower().endswith(".zip"):
            return service.create_scenario(db, name, service.read_zip(await files[0].read()), "upload:zip")
        for f in files:
            raw = await f.read()
            try:
                content[Path(f.filename or "").name] = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise ApiError(422, "bad_encoding", f"{f.filename} is not UTF-8 text")
        return service.create_scenario(db, name, content, "upload")

    @app.post("/api/scenarios/sample")
    def sample(req: SampleRequest):
        return service.create_sample(db, req.name)

    @app.get("/api/scenarios")
    def scenarios():
        return service.list_scenarios(db)

    @app.get("/api/scenarios/{sid}")
    def scenario(sid: int):
        return service.scenario_detail(db, sid)

    @app.post("/api/scenarios/{sid}/runs")
    def run(sid: int, req: RunRequest):
        d = service.scenario_detail(db, sid)
        if not d["valid"]:
            raise ApiError(422, "invalid_data", "The data has errors; fix them before running.",
                           [i for i in d["issues"] if i["severity"] == "error"])
        return service.create_run(db, sid, req.mode, req.time_limit)

    @app.get("/api/scenarios/{sid}/runs")
    def runs(sid: int):
        return service.list_runs(db, sid)

    @app.post("/api/scenarios/{sid}/whatif")
    def whatif(sid: int, req: WhatIfRequest):
        service.scenario_detail(db, sid)
        return service.run_whatif(db, sid, req.changes, req.mode, req.time_limit, req.actor, req.reference_run_id)

    # ----- runs -----
    @app.get("/api/runs/{rid}")
    def run_detail(rid: int):
        return service.run_detail(db, rid)

    @app.post("/api/runs/{rid}/overrides")
    def override(rid: int, req: OverrideRequest):
        return service.apply_override(db, rid, req.zone, req.sku, req.warehouse, req.pallets, req.reason, req.actor)

    @app.post("/api/runs/{rid}/explanation")
    def make_explanation(rid: int, req: ExplainRequest | None = None):
        return service.generate_explanation(db, rid, get_llm(), use_llm=bool(req and req.use_llm))

    @app.get("/api/runs/{rid}/explanation")
    def get_explanation(rid: int):
        service.run_detail(db, rid)
        return service.explanation_detail(db, rid) or {"run_id": rid, "text": None}

    @app.post("/api/runs/{rid}/explanation/approve")
    def approve_explanation(rid: int, req: ApproveExplanation):
        return service.approve_explanation(db, rid, req.text, req.actor)

    @app.post("/api/runs/{rid}/decision")
    def decision(rid: int, req: Decision):
        return service.decide(db, rid, req.decision, req.comment, req.actor)

    @app.get("/api/runs/{rid}/export")
    def export(rid: int):
        data = service.export_zip(db, rid)
        return Response(content=data, media_type="application/zip",
                        headers={"Content-Disposition": f'attachment; filename="nordic-flow-run-{rid}.zip"'})

    # ----- audit and mapping -----
    @app.get("/api/audit")
    def audit_log(run_id: int | None = None, scenario_id: int | None = None):
        return audit.events(db, run_id=run_id, scenario_id=scenario_id)

    @app.get("/api/audit/verify")
    def audit_verify():
        return audit.verify_chain(db)

    @app.post("/api/mapping/suggest")
    def mapping(req: MappingRequest):
        client = get_llm() if req.use_llm else None
        return suggest(req.items, service.scenario_dataset(db, req.scenario_id), client=client)

    @app.post("/api/mapping/confirm")
    def mapping_confirm(req: MappingConfirm):
        ds = service.scenario_dataset(db, req.scenario_id)
        if req.sku_id not in ds.skus:
            raise ApiError(422, "unknown_sku", f"unknown SKU {req.sku_id!r}")
        audit.record(db, "MAPPING_CONFIRMED", req.actor, req.scenario_id, None,
                     {"external": req.external, "sku_id": req.sku_id, "sku_name": ds.skus[req.sku_id].name})
        return {"confirmed": True}

    if WEB.exists():
        app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
    app.state.db = db
    return app


app = create_app()
