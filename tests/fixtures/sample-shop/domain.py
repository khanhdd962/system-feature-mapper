"""Small executable in-memory shop domain; synthetic data only."""
class Shop:
    def __init__(self):
        self.stock = {'book': 2}
        self.orders = []
        self.signed_in = False

    def login(self, username, password):
        if not username or not password:
            raise ValueError('Vui lòng nhập tên và mật khẩu')
        # Demonstration credentials; no production identity provider.
        if username != 'demo' or password != 'demo':
            raise PermissionError('Thông tin đăng nhập không đúng')
        self.signed_in = True
        return 'Đăng nhập thành công'

    def logout(self):
        self.signed_in = False
        return 'Đã đăng xuất'

    def purchase(self, product, quantity):
        if not self.signed_in:
            raise PermissionError('Cần đăng nhập')
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError('Số lượng phải là số nguyên dương')
        if product not in self.stock:
            raise ValueError('Không tìm thấy sản phẩm')
        if self.stock[product] < quantity:
            raise ValueError('Không đủ hàng')
        order = {'id': len(self.orders) + 1, 'product': product, 'quantity': quantity, 'status': 'new'}
        self.stock[product] -= quantity
        self.orders.append(order)
        return order['id']

    def history(self):
        if not self.signed_in:
            raise PermissionError('Cần đăng nhập')
        return [dict(order) for order in self.orders]

    def cancel(self, order_id):
        if not self.signed_in:
            raise PermissionError('Cần đăng nhập')
        order = next((o for o in self.orders if o['id'] == order_id), None)
        if order is None:
            raise ValueError('Không tìm thấy đơn')
        if order['status'] != 'new':
            raise ValueError('Chỉ hủy đơn mới')
        order['status'] = 'cancelled'
        self.stock[order['product']] += order['quantity']
        return 'Đã hủy đơn'
