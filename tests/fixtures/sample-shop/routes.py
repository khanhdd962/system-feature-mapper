# Declarative demo routes. No web server or external dependency.
ROUTES = {
    '/account/login': ('POST', 'login'),
    '/account/logout': ('POST', 'logout'),
    '/shop/purchase': ('POST', 'purchase'),
    '/orders': ('GET', 'history'),
    '/orders/cancel': ('POST', 'cancel'),
}
