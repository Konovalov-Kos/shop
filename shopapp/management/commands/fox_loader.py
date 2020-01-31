import json

from django.core.management.base import BaseCommand, CommandError
from shopapp.parther import *
from shopapp.models import *
class Command(BaseCommand):
    help = 'copy-past in foxtrot'

    def handle(self, *args, **options):
        trea = parse_treas(url1)
        Product.objects.all().delete()
        def ceate_cat(cat, parent=None):
            for i, j in cat.items():
                link = j.pop('href', None)
                if Category.objects.filter(name=i).exists():
                    dady = Category.objects.filter(name=i).first()
                else:
                    dady = Category.objects.create(name=i, parent=parent)
                if link:
                    links = parse_urls_items(link)
                    for link in links:
                        #print(link)
                        prod = parse_items(link)
                        if not prod:
                            continue
                        prod['category_id'] = dady.id
                        brand_name = prod.pop('brand')
                        if not Brand.objects.filter(name=brand_name).exists():
                            brand = Brand.objects.create(name=brand_name)
                        else:
                            brand = Brand.objects.filter(name=brand_name)[0]
                        prod['brand_id'] = brand.id
                        if not Product.objects.filter(name=prod['name']).exists():
                            Product.objects.create(**prod)
                            # pr = Product.objects.create(name=prod['name'],
                            #                        price=prod['price'],
                            #                        prev_price=prod['prev_price'],
                            #                        image=prod['image'],
                            #                        category_id=prod['category_id'],
                            #                        brand_id=prod['brand_id'],
                            #
                            #                        )
                            # pr.description = 'descr'
                            # pr.specification = 'cpec'
                            # pr.save()
                    return
                if type(j) == dict:
                    ceate_cat(j, parent=dady)
        ceate_cat(trea)
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))