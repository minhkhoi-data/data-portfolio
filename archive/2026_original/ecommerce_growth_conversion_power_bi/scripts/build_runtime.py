"""Create a CSV integrity manifest and a uniquely named native entry point."""
import json,shutil
from pipeline import ROOT,TABLES,sha256

def main():
    files=[]
    for name in [*TABLES.values(),'funnel_stage','measures']:
        file=ROOT/'data'/f'{name}.csv'
        files.append({'path':file.relative_to(ROOT).as_posix(),'bytes':file.stat().st_size,'sha256':sha256(file)})
    manifest={'release':'GA4_CSV_REBUILD_2026_10_13','files':files,'note':'CSV bytes are checked before the local DataFolder parameter is set. No Desktop success is asserted.'}
    (ROOT/'runtime_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'BAT_DAU.txt').write_text('''GA4 - bản dựng CSV ngày 13/10/2026

1. Giải nén toàn bộ ZIP vào folder mới.
2. Bấm đúp MO_PROJECT.cmd để đặt đường dẫn và mở Power BI.
3. Bấm Home > Refresh trong Power BI, chờ nạp xong, rồi chụp Executive Overview.

Tám CSV đã nằm sẵn trong data/. Không cần tự chép thêm CSV hay sửa DAX.
Giữ nguyên data/, scripts/, powerbi/ và runtime_manifest.json.
Nếu Windows không tự mở PBIP, sau khi chạy MO_PROJECT.cmd hãy dùng
Power BI > File > Open > powerbi/MO_GA4_CSV_13_10.pbip.

Bản dựng có kiểm tra dữ liệu và cấu trúc tĩnh. Trạng thái cú pháp, schema và bằng chứng ứng dụng gốc được ghi riêng trong audit/evidence/build_status.json và audit/NATIVE_STATUS.md.
Chưa chạy được Power BI Desktop ở môi trường dựng; vẫn cần xác nhận
mở và Refresh thực tế trên máy ông. Đây không phải cam kết đã hết lỗi native.
''',encoding='utf-8')
    target=ROOT/'powerbi/MO_GA4_CSV_13_10.pbip'
    target.write_text(json.dumps({'version':'1.0','artifacts':[{'report':{'path':'EcommerceGrowth.Report'}}],'settings':{'enableAutoRecovery':True}},indent=2)+'\n')
    for original in (ROOT/'powerbi').glob('*.pbip'):
        if original!=target:original.unlink()
    obsolete=ROOT/'scripts/package_patch.py'
    if obsolete.exists():obsolete.unlink()
    for cache in (ROOT/'powerbi').rglob('.pbi'):shutil.rmtree(cache)
    print('PASS: runtime CSV manifest, clean cache and unique PBIP entry created')

if __name__=='__main__':main()
