import { useState } from "react";
import { Download } from "lucide-react";
import { useApp } from "../store.jsx";
import { PageHead } from "../components/ui.jsx";

const FILES = [
  { name: "suppliers.csv", purpose: "Danh sách xưởng / nhà cung cấp", columns: [
    ["supplier_id", "Chuỗi", "Mã duy nhất, ví dụ SUP1. Dùng đúng mã này trong các file cước và nguồn cung."],
    ["name", "Chuỗi", "Tên hiển thị của xưởng / nhà cung cấp."],
  ], csv: "supplier_id,name\nSUP1,Factory" },
  { name: "warehouses.csv", purpose: "Tất cả kho, bao gồm kho trung gian", columns: [
    ["warehouse_id", "Chuỗi", "Mã kho duy nhất. Tên/mã A hay E không quyết định thứ tự đi qua kho."],
    ["name", "Chuỗi", "Tên kho hiển thị trên sơ đồ."],
    ["capacity_pallets", "Số ≥ 0", "Năng lực nhận hàng trong cùng kỳ, tính bằng pallet-equivalent. 0 là đóng kho. Lượng nhận × pallet_factor tiêu thụ năng lực này."],
    ["handling_in", "Số ≥ 0", "Phí nhận một pallet tại kho, gồm hàng nhận từ xưởng và kho khác."],
    ["handling_out", "Số ≥ 0", "Phí xuất một pallet tại kho, gồm giao đến kho khác hoặc khách."],
  ], csv: "warehouse_id,name,capacity_pallets,handling_in,handling_out\nW01,Warehouse 1,10,1,1\nW02,Warehouse 2,10,1,1" },
  { name: "zones.csv", purpose: "Vùng khách hàng và kho ưu tiên của baseline", columns: [
    ["zone_id", "Chuỗi", "Mã vùng khách duy nhất, ví dụ Z1."],
    ["name", "Chuỗi", "Tên khách / vùng khách hiển thị."],
    ["preferred_warehouse", "Mã kho", "Kho giao cuối được baseline ưu tiên; không ép bộ tối ưu chọn kho này. Với vùng chỉ giao thẳng, không có tuyến kho → khách, giữ cột nhưng có thể để giá trị trống."],
  ], csv: "zone_id,name,preferred_warehouse\nZ1,Customer,W02", note: "Ví dụ chỉ giao thẳng: Z1,Customer, (dấu phẩy cuối giữ giá trị preferred_warehouse trống)." },
  { name: "skus.csv", purpose: "Danh mục sản phẩm", columns: [
    ["sku_id", "Chuỗi", "Mã sản phẩm duy nhất, ví dụ SKU-01."],
    ["name", "Chuỗi", "Tên sản phẩm hiển thị."],
    ["pallet_factor", "Số > 0", "Năng lực kho mà một pallet sản phẩm sử dụng. Ví dụ factor 2: nhận 10 pallet dùng 20 đơn vị năng lực tại mỗi kho đi qua."],
  ], csv: "sku_id,name,pallet_factor\nSKU-01,Example product,1" },
  { name: "inbound_rates.csv", purpose: "Các tuyến xưởng → kho được phép", columns: [
    ["supplier_id", "Mã xưởng", "Tham chiếu suppliers.csv."], ["warehouse_id", "Mã kho", "Tham chiếu warehouses.csv."],
    ["cost_per_pallet", "Số ≥ 0", "Cước vận chuyển một pallet trên riêng chặng này; chưa gồm phí xử lý tại kho."],
  ], csv: "supplier_id,warehouse_id,cost_per_pallet\nSUP1,W01,2" },
  { name: "outbound_rates.csv", purpose: "Các tuyến kho → khách được phép", columns: [
    ["warehouse_id", "Mã kho", "Kho làm chặng giao cuối."], ["zone_id", "Mã khách", "Tham chiếu zones.csv."],
    ["cost_per_pallet", "Số ≥ 0", "Cước vận chuyển một pallet từ kho đến vùng khách; chưa gồm phí xuất kho."],
  ], csv: "warehouse_id,zone_id,cost_per_pallet\nW02,Z1,3" },
  { name: "supply.csv", purpose: "Nguồn cung tối đa theo xưởng và sản phẩm", columns: [
    ["supplier_id", "Mã xưởng", "Tham chiếu suppliers.csv."], ["sku_id", "Mã sản phẩm", "Tham chiếu skus.csv."],
    ["max_pallets", "Số ≥ 0", "Tổng lượng xưởng có thể cấp trong kỳ, dùng chung cho giao thẳng và đi qua kho. Whole pallets làm tròn xuống nguồn cung lẻ và báo cảnh báo."],
  ], csv: "supplier_id,sku_id,max_pallets\nSUP1,SKU-01,10" },
  { name: "demand.csv", purpose: "Nhu cầu khách theo sản phẩm", columns: [
    ["zone_id", "Mã khách", "Tham chiếu zones.csv."], ["sku_id", "Mã sản phẩm", "Tham chiếu skus.csv."],
    ["pallets", "Số ≥ 0", "Nhu cầu phải giao đủ trong kỳ. Whole pallets yêu cầu số nguyên; Fractional pallets cho phép số lẻ."],
  ], csv: "zone_id,sku_id,pallets\nZ1,SKU-01,10" },
  { name: "transfer_rates.csv", optional: true, purpose: "Kho → kho, cần khi có nhiều kho nối tiếp", columns: [
    ["from_warehouse_id", "Mã kho", "Kho xuất hàng."], ["to_warehouse_id", "Mã kho", "Kho nhận hàng; phải khác kho xuất."],
    ["cost_per_pallet", "Số ≥ 0", "Cước của chặng chuyển kho. Hệ thống cộng thêm handling_out tại kho xuất và handling_in tại kho nhận."],
    ["max_pallets", "Tùy chọn: số ≥ 0", "Giới hạn tuyến trong kỳ, cộng trên tất cả SKU. Bỏ cột hoặc để ô trống là không có giới hạn riêng của tuyến; 0 là đóng tuyến. Năng lực kho vẫn áp dụng."],
  ], csv: "from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets\nW01,W02,1,10", note: "Tuyến có hướng. W01 → W02 không tự tạo W02 → W01. Mạng chuyển kho phải không có vòng lặp, kể cả các tuyến có max_pallets bằng 0." },
  { name: "direct_rates.csv", optional: true, purpose: "Xưởng → khách, không đi qua kho", columns: [
    ["supplier_id", "Mã xưởng", "Xưởng giao thẳng đến khách."], ["zone_id", "Mã khách", "Vùng khách nhận trực tiếp."],
    ["cost_per_pallet", "Số ≥ 0", "Toàn bộ cước chặng xưởng → khách. Không phát sinh phí xử lý hoặc tiêu thụ năng lực kho."],
    ["max_pallets", "Tùy chọn: số ≥ 0", "Giới hạn giao thẳng của tuyến, dùng chung cho tất cả SKU. Trống/bỏ cột là không giới hạn riêng; 0 đóng tuyến. Nguồn cung và nhu cầu vẫn giới hạn lượng hàng."],
  ], csv: "supplier_id,zone_id,cost_per_pallet,max_pallets\nSUP1,Z1,7,10", note: "Thiếu file này nghĩa là không cho giao thẳng. Trường hợp hoàn toàn không dùng kho vẫn phải gửi đủ 8 file bắt buộc; warehouses.csv, inbound_rates.csv, outbound_rates.csv chỉ cần dòng tiêu đề." },
  { name: "warehouse_skus.csv", optional: true, purpose: "Giới hạn sản phẩm mỗi kho được nhận", columns: [
    ["warehouse_id", "Mã kho", "Kho được phép nhận sản phẩm này."], ["sku_id", "Mã sản phẩm", "SKU được phép tại kho; một cặp trên một dòng."],
  ], csv: "warehouse_id,sku_id\nW01,SKU-01\nW02,SKU-01", note: "Không có file: mọi SKU được phép ở mọi kho. Có file: chỉ những cặp được liệt kê mới được phép; kho bị bỏ sót không nhận SKU nào. Quy tắc áp dụng ở mọi kho trung gian; giao thẳng không dùng kho." },
];

const CASES = [
  ["10_direct_factory_customer.zip", "Không qua kho", "Xưởng → Khách", "70", "70"],
  ["11_chain_3_warehouses.zip", "Qua 3 kho", "Xưởng → W01 → W02 → W03 → Khách", "130", "130"],
  ["12_chain_4_warehouses.zip", "Qua 4 kho", "Xưởng → W01 → … → W04 → Khách", "160", "160"],
  ["13_chain_5_warehouses.zip", "Qua 5 kho", "Xưởng → W01 → … → W05 → Khách", "190", "190"],
  ["14_chain_8_warehouses.zip", "Qua 8 kho", "Xưởng → W01 → … → W08 → Khách", "280", "280"],
  ["15_chain_12_warehouses.zip", "Qua 12 kho", "Xưởng → W01 → … → W12 → Khách", "400", "400"],
  ["16_mixed_direct_chain_5.zip", "Giao thẳng + qua 5 kho", "3 pallet giao thẳng, 7 pallet qua W01…W05", "190", "145"],
];

function InputGuide() {
  return <>
    <div className="card card-pad">
      <h3 className="text-lg font-semibold text-slate-900">Định dạng gửi lên hệ thống</h3>
      <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-relaxed text-slate-600">
        <li>Gửi <b>đủ 8 CSV bắt buộc cùng lúc</b>, hoặc một ZIP chứa các CSV đó. Có thể thêm 3 CSV tùy chọn bên dưới.</li>
        <li>File phải là <b>CSV UTF-8</b> (có hoặc không BOM), ngăn cột bằng dấu phẩy, dòng đầu là tên cột chính xác. Mỗi dòng dữ liệu có cùng số ô với tiêu đề. File Excel .xlsx không được đọc trực tiếp.</li>
        <li>Số thập phân dùng dấu chấm: <code>12.5</code>. Không thêm đơn vị tiền, ký hiệu % hay dấu phân nhóm hàng nghìn. Không dùng số âm, NaN hoặc infinity.</li>
        <li>Mã xưởng/kho/khách/SKU phải khớp giữa các file và phân biệt chữ hoa/thường. Một khóa hoặc tuyến chỉ khai báo một dòng; không tự suy ra tuyến bị thiếu.</li>
        <li>Trong ZIP, các CSV nằm <b>ngay thư mục gốc</b>, không bọc trong folder, không thêm ảnh hay báo cáo. Tên file đúng như bảng bên dưới.</li>
        <li>Giới hạn ZIP: tổng dữ liệu sau giải nén tối đa 5.000.000 byte, mỗi CSV tối đa 2.000.000 byte. Tất cả số liệu thuộc cùng một kỳ kế hoạch và cùng đơn vị tiền.</li>
      </ol>
      <p className="hint mt-3">Trong Excel, lưu dạng CSV UTF-8 (Comma delimited). Nếu máy xuất dấu chấm phẩy, chuyển sang dấu phẩy. Giá trị chứa dấu phẩy cần đặt trong dấu nháy kép, ví dụ <code>SUP1,"Factory, North"</code>.</p>
      <a className="btn btn-secondary mt-4" href="/examples/13_chain_5_warehouses.zip" download><Download size={15} aria-hidden="true" />Tải bộ CSV mẫu hợp lệ</a>
    </div>
    <div className="mt-5 flex flex-wrap items-center gap-3 text-sm"><b className="text-slate-900">8 file bắt buộc + 3 file tùy chọn</b><span className="text-slate-500">Mở từng mục để xem cột, ý nghĩa và ví dụ.</span></div>
    <div className="mt-3 space-y-3">{FILES.map(file => <details key={file.name} className="card">
      <summary className="cursor-pointer px-5 py-4"><code className="text-sm font-semibold text-brand-800">{file.name}</code><span className="ml-3 text-xs text-slate-500">{file.optional ? "Tùy chọn" : "Bắt buộc"}</span><span className="mt-1 block pl-4 text-sm text-slate-600">{file.purpose}</span></summary>
      <div className="border-t border-slate-100 px-5 py-4">
        <div className="overflow-x-auto"><table className="tbl"><thead><tr><th>Cột</th><th>Kiểu</th><th>Ý nghĩa và quy tắc</th></tr></thead><tbody>{file.columns.map(([name, type, description]) => <tr key={name}><td><code>{name}</code></td><td className="whitespace-nowrap">{type}</td><td>{description}</td></tr>)}</tbody></table></div>
        <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">Ví dụ nội dung CSV</p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">{file.csv}</pre>
        {file.note && <p className="mt-3 text-sm leading-relaxed text-amber-900">{file.note}</p>}
      </div>
    </details>)}</div>
    <div className="card card-pad mt-5"><h3 className="font-semibold text-slate-900">Cách tính cho nhiều kho</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">Đường đi qua N kho có N − 1 chặng chuyển kho. Tổng tiền = cước xưởng → kho đầu + tất cả cước kho → kho + cước kho cuối → khách + phí nhận/xuất tại từng kho. Một pallet đi qua 5 kho bị tính phí nhận và xuất ở cả 5 kho, đồng thời dùng năng lực nhận hàng tại từng kho. Không có giới hạn cố định 3 hay 5 kho trong mô hình; các tuyến phải nối được tới khách và không tạo vòng lặp.</p></div>
  </>;
}

function WorkflowGuide() {
  const steps = [
    ["1. Data — tải và kiểm tra", "Chọn mẫu hoặc upload đầy đủ CSV/ZIP rồi bấm Upload and check. Sửa lỗi theo tên file/cột/dòng trước khi Calculate plan. Change data mở lại phần chọn nguồn. Whole pallets chỉ dùng số pallet nguyên; Fractional pallets cho phép chia lẻ để so mốc chi phí khi nới điều kiện nguyên."],
    ["2. Results — đọc phương án", "KPI hiển thị tổng tiền, baseline, tiết kiệm và kết quả kiểm tra. Baseline là quy tắc ưu tiên kho giao cuối, không phải kế hoạch thực tế do doanh nghiệp cung cấp. Với tuyến giao thẳng, baseline dùng trực tiếp khi các lựa chọn kho không phục vụ hết. OPTIMAL là đã chứng minh tối ưu; FEASIBLE là phương án tốt nhất tìm được trong thời gian cho phép."],
    ["3. Sơ đồ và bảng xếp hạng", "Nét màu là chặng đang có hàng, nét xám đứt là lựa chọn chưa dùng, nét đỏ đứt là chặng hiện bị chặn. Độ dày đo lượng hàng, không đo giá. Bấm một chặng xem cước/phí của riêng chặng đó; bảng Complete route cost ranking tính cả đường từ xưởng tới khách. Lọc khách/SKU, nhập lượng so sánh rồi chọn dòng để tô cam đường đó. Highlight chỉ đổi cách nhìn, không đổi phương án."],
    ["4. Create manual route — chọn đường theo quyết định con người", "Mở màn chỉnh tuyến riêng. Chọn xưởng, khách, SKU, loại giao và các kho theo thứ tự (nếu có), số pallet và lý do. Save route and recalculate tạo phiên bản con, giữ bản gốc, tối ưu phần hàng còn lại và hiển thị chênh lệch tổng tiền. Back to Results không lưu form chưa gửi. Lượng được dành trước là tối thiểu; phần còn lại có thể dùng thêm các chặng đó. Xóa ràng buộc bằng Remove route constraint."],
    ["5. Chỉ đổi kho giao cuối", "Trong Review & approve, mở Adjust plan → Change delivery warehouse. Chọn Serve from, số pallet và lý do. Đây là ghim chính xác lượng giao từ kho cuối; hệ thống vẫn chọn lại nguồn và kho trung gian. Chức năng này dành cho đường có kho."],
    ["6. Review & approve — giải thích và duyệt", "Write standard summary tạo văn bản từ số liệu đã tính. Write with AI assistant dùng Groq khi server có cấu hình, vẫn cần đọc và kiểm tra ý nghĩa. Kiểm tra số không đảm bảo AI đúng mọi diễn giải. Approve explanation và Approve plan là hai thao tác riêng. Sau duyệt mới hiện Export approved plan (ZIP); kế hoạch đã duyệt/từ chối bị khóa chỉnh sửa. Version history mở lại bản cũ cùng giải thích đã lưu."],
    ["7. What-if và Audit trail", "What-if thử đóng kho, đổi năng lực hoặc nhu cầu trên bản sao, rồi so với phương án gốc. Đóng kho không chặn tuyến xưởng → khách vì tuyến đó không dùng kho. Audit trail lưu các lần tải dữ liệu, tính, chọn tuyến, duyệt và xuất. Start a new version tính bản mới khi cần thay đổi kế hoạch đã khóa."],
  ];
  return <div className="space-y-4">{steps.map(([title, description]) => <div className="card card-pad" key={title}><h3 className="font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p></div>)}</div>;
}

function SamplesGuide() {
  return <div className="card card-pad"><h3 className="text-lg font-semibold text-slate-900">Bộ testcase tải lên chạy ngay</h3><p className="mt-2 text-sm leading-relaxed text-slate-600">Mỗi ZIP chứa bộ CSV hoàn chỉnh ở thư mục gốc. Tải một ZIP, vào Data → Change data (nếu đã có dữ liệu) → Upload files → Upload and check → Calculate plan. Các mẫu dùng 10 pallet, pallet_factor = 1 và chi phí giả lập để đối chiếu.</p>
    <div className="mt-4 overflow-x-auto"><table className="tbl"><thead><tr><th>Mẫu</th><th>Đường đi</th><th className="num">Baseline</th><th className="num">Tối ưu</th><th /></tr></thead><tbody>{CASES.map(([file, title, route, baseline, optimum]) => <tr key={file}><td className="font-medium">{title}</td><td>{route}</td><td className="num">{baseline}</td><td className="num">{optimum}</td><td><a className="text-brand-800 underline" href={`/examples/${file}`} download aria-label={`Download ${file}`}>Tải ZIP</a></td></tr>)}</tbody></table></div>
    <p className="mt-4 text-sm leading-relaxed text-slate-600">Chuỗi N kho: cước đầu 2, mỗi chuyển kho 1, cước cuối 3, mỗi kho nhận 1 và xuất 1. Giá một pallet là 3N + 4. Ví dụ 5 kho: 19 × 10 = 190. Mẫu hỗn hợp có tuyến giao thẳng giá 4 nhưng giới hạn 3 pallet, nên 3 × 4 + 7 × 19 = 145.</p>
  </div>;
}

function QuestionsGuide() {
  const questions = [
    ["Vì sao chưa tính được?", "Kiểm tra đã tải đủ file, đúng tên cột và mã tham chiếu. Lỗi đỏ chặn chạy; cảnh báo cần đọc. Dữ liệu hợp lệ về định dạng vẫn có thể không có phương án đủ cung/cầu/năng lực. Hệ thống sẽ báo không khả thi, không tự bịa đường hay cước."],
    ["Vì sao đường rẻ nhất không chở hết?", "Kho, tuyến và nguồn cung có giới hạn dùng chung. Xếp hạng là giá cả đường cho mỗi pallet; Standalone limit là giới hạn khi dùng đường đó riêng. Exceeds limit nghĩa là lượng so sánh vượt mức ấy. Bộ tối ưu có thể phải chia hàng qua nhiều đường để tổng tiền thấp nhất."],
    ["Tên kho có cố định thứ tự không?", "Không. Có thể E → A nếu input khai báo đủ các chặng. Mạng chuyển kho hiện không hỗ trợ vòng A → E → A. Tất cả chặng hoàn thành trong cùng kỳ; chưa mô hình lịch giao, tồn kho qua kỳ hay thời gian di chuyển."],
    ["Giá nội bộ hoặc ưu tiên đối tác được nhập ở đâu?", "Giá thật nhập vào cost_per_pallet của chặng tương ứng rồi tải bộ dữ liệu mới. Quyết định dùng một đường vì quan hệ/hợp đồng được nhập ở Create manual route kèm lý do. Phần lý do không tự tạo chiết khấu."],
    ["Có biết từng pallet vật lý đi đường nào không?", "MVP tính tổng luồng theo SKU. Khi hàng gộp/tách qua kho, Plan breakdown là một cách phân rã để giải thích tiền, không xác nhận danh tính từng pallet. Các đường thủ công được dành lượng trước khi phân rã phần còn lại."],
    ["Tôi có thể tải riêng một CSV để thay một cước không?", "Mỗi upload là một scenario mới; cần gửi lại đủ bộ 8 file bắt buộc và các file tùy chọn đang dùng. Có thể sửa cước trong ZIP đã tải mẫu, nén lại đúng cấu trúc rồi upload."],
  ];
  return <div className="space-y-3">{questions.map(([question, answer]) => <details className="card" key={question}><summary className="cursor-pointer px-5 py-4 text-sm font-semibold text-slate-900">{question}</summary><p className="border-t border-slate-100 px-5 py-4 text-sm leading-relaxed text-slate-600">{answer}</p></details>)}</div>;
}

export default function GuideView() {
  const { go } = useApp();
  const [tab, setTab] = useState("input");
  const tabs = [["input", "Định dạng input"], ["workflow", "Cách sử dụng"], ["samples", "Testcase mẫu"], ["questions", "Câu hỏi thường gặp"]];
  return <div>
    <PageHead title="User guide" lead="Hướng dẫn sử dụng và chuẩn bị dữ liệu cho Nordic Flow."><button type="button" className="btn btn-secondary" onClick={() => go("data")}>Go to Data</button></PageHead>
    <nav className="mb-5 flex flex-wrap gap-2" aria-label="Guide sections">{tabs.map(([id, label]) => <button type="button" key={id} aria-pressed={tab === id} className={`btn ${tab === id ? "btn-primary" : "btn-secondary"}`} onClick={() => setTab(id)}>{label}</button>)}</nav>
    {tab === "input" ? <InputGuide /> : tab === "workflow" ? <WorkflowGuide /> : tab === "samples" ? <SamplesGuide /> : <QuestionsGuide />}
  </div>;
}
