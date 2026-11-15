# Hủy đơn mới

Hủy đơn mới và hoàn số lượng sách về tồn kho.

## Người dùng

- Khách dùng bản mẫu

## Điều kiện

- Đã đăng nhập.
- Đơn tồn tại và còn mới.

## Cách sử dụng

- Nhập mã đơn.
- Chọn Hủy đơn.

## Đầu vào

- Mã đơn.

## Kết quả

- Thông báo đã hủy đơn.
- Đơn đã hủy và tồn kho được hoàn.

## Luồng chính

- Kiểm tra đăng nhập, tìm đơn và kiểm tra trạng thái mới.
- Chuyển đơn sang đã hủy và tăng lại tồn kho.

## Luồng thay thế

Source bản mẫu không mô tả nội dung này ở mức chức năng hiện tại.

## Ngoại lệ

- Chưa đăng nhập: từ chối.
- Không tìm thấy mã đơn: báo lỗi.
- Đơn không còn mới: không cho hủy.

## Xác minh

source_confirmed
Đã đối chiếu source bản mẫu; chưa quan sát ứng dụng web chạy.
