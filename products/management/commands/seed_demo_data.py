"""
Load sample Users, Categories, Products, Profiles, Orders, and Payments for docs / screenshots.

Usage:
  python manage.py seed_demo_data
  python manage.py seed_demo_data --clear   # remove previous seed, then insert again

Demo logins (password for all): demo123
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from payments.models import Payment
from products.models import Category, Order, Product, Profile

DEMO_USERNAMES = ('demo_alice', 'demo_bob', 'demo_carol')

SEED_CATEGORIES = [
    {'name': 'Electronics', 'description': 'Phones, laptops, and accessories'},
    {'name': 'Books', 'description': 'Fiction, technical, and study material'},
    {'name': 'Home & Kitchen', 'description': 'Furniture, appliances, cookware'},
    {'name': 'Apparel', 'description': 'Clothing and footwear'},
]

SEED_PRODUCTS = [
    ('Wireless Earbuds Pro', 'ANC earbuds, 30h battery', 4999.0, 'Electronics'),
    ('USB-C Hub 7-in-1', 'HDMI, SD, USB 3.0', 2499.0, 'Electronics'),
    ('Backend Systems Handbook', 'Distributed systems primer', 899.0, 'Books'),
    ('Python Cookbook', 'Recipes for Django & DRF', 1299.0, 'Books'),
    ('Ceramic Cookware Set', 'Non-stick, induction safe', 3499.0, 'Home & Kitchen'),
    ('Cotton Tee — Navy', 'Regular fit, size M–XL', 799.0, 'Apparel'),
    ('Running Shoes', 'Lightweight mesh, size 7–11', 4499.0, 'Apparel'),
]

SEED_PROFILES = {
    'demo_alice': ('+91 98765 43210', '12 MG Road, Bengaluru, KA 560001'),
    'demo_bob': ('+91 91234 56789', '45 Park Street, Kolkata, WB 700016'),
    'demo_carol': ('+91 99887 76655', '88 FC Road, Pune, MH 411004'),
}


class Command(BaseCommand):
    help = 'Insert demo users, categories, products, profiles, orders, and payments for documentation screenshots.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove data from a previous seed run, then insert fresh rows.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()
        self._seed()
        self.stdout.write(self.style.SUCCESS(
            'Demo data ready. Open /admin/ as a superuser (e.g. admin) to screenshot Users, Categories, '
            'Products, Orders, Profiles, Payments. Demo customer accounts (password demo123): demo_alice, demo_bob, demo_carol.'
        ))

    def _clear(self):
        User.objects.filter(username__in=DEMO_USERNAMES).delete()
        product_names = [p[0] for p in SEED_PRODUCTS]
        Product.objects.filter(name__in=product_names).delete()
        category_names = [c['name'] for c in SEED_CATEGORIES]
        Category.objects.filter(name__in=category_names).delete()
        self.stdout.write('Cleared previous demo seed.')

    def _seed(self):
        users = {}
        for username in DEMO_USERNAMES:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.replace('demo_', '').title(),
                    'is_staff': False,
                },
            )
            u.set_password('demo123')
            u.save()
            users[username] = u
            self.stdout.write(f"{'Created' if created else 'Updated'} user {username}")

        for cat in SEED_CATEGORIES:
            Category.objects.get_or_create(
                name=cat['name'],
                defaults={'description': cat['description']},
            )

        products = {}
        for name, desc, price, cat_name in SEED_PRODUCTS:
            cat = Category.objects.get(name=cat_name)
            p, _ = Product.objects.update_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'price': price,
                    'category': cat,
                    'is_available': True,
                },
            )
            products[name] = p

        for username, (phone, addr) in SEED_PROFILES.items():
            user = users[username]
            Profile.objects.update_or_create(
                user=user,
                defaults={'phone_number': phone, 'address': addr},
            )

        if not Order.objects.filter(order_number='DEMO-ORD-1001').exists():
            o1 = Order.objects.create(
                user=users['demo_alice'],
                status='CONFIRMED',
                total_amount=4999.0,
                order_number='DEMO-ORD-1001',
            )
            o1.products.add(products['Wireless Earbuds Pro'])
            self.stdout.write('Created order DEMO-ORD-1001')

        if not Order.objects.filter(order_number='DEMO-ORD-1002').exists():
            o2 = Order.objects.create(
                user=users['demo_bob'],
                status='SHIPPED',
                total_amount=3798.0,
                order_number='DEMO-ORD-1002',
            )
            o2.products.add(products['Python Cookbook'], products['Cotton Tee — Navy'])
            self.stdout.write('Created order DEMO-ORD-1002')

        if not Order.objects.filter(order_number='DEMO-ORD-1003').exists():
            o3 = Order.objects.create(
                user=users['demo_carol'],
                status='PENDING',
                total_amount=4499.0,
                order_number='DEMO-ORD-1003',
            )
            o3.products.add(products['Running Shoes'])
            self.stdout.write('Created order DEMO-ORD-1003')

        # amount in paise (integer)
        demo_payments = [
            {
                'payment_id': 'demo_pay_success_001',
                'order_id': 'DEMO-ORD-1001',
                'user': users['demo_alice'],
                'amount': 499900,
                'status': 'SUCCESS',
                'payment_method': 'UPI',
                'gateway_payment_id': 'pay_RzDemoSuccess01',
                'gateway_order_id': 'order_RzDemo01',
                'webhook_received': True,
            },
            {
                'payment_id': 'demo_pay_pending_002',
                'order_id': 'DEMO-ORD-1003',
                'user': users['demo_carol'],
                'amount': 449900,
                'status': 'PENDING',
                'payment_method': 'RAZORPAY',
                'gateway_order_id': 'order_RzDemoPending02',
                'webhook_received': False,
            },
            {
                'payment_id': 'demo_pay_failed_003',
                'order_id': 'DEMO-ORD-1002',
                'user': users['demo_bob'],
                'amount': 379800,
                'status': 'FAILED',
                'payment_method': 'CREDIT_CARD',
                'webhook_received': True,
            },
            {
                'payment_id': 'demo_pay_refund_004',
                'order_id': 'DEMO-ORD-1002',
                'user': users['demo_bob'],
                'amount': 129900,
                'status': 'REFUNDED',
                'payment_method': 'RAZORPAY',
                'gateway_payment_id': 'pay_RzDemoRefund04',
                'webhook_received': True,
            },
        ]

        for row in demo_payments:
            pid = row['payment_id']
            if not Payment.objects.filter(payment_id=pid).exists():
                Payment.objects.create(**row)
                self.stdout.write(f'Created payment {pid}')
