from django.core.management.base import BaseCommand, CommandError

from bigfish.apps.public.models import Public


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-A', nargs='+', type=int)
        # app 名称
        parser.add_argument(
            '-a',
            '--app',
            action='store_true',
            dest='app',
            default=False,
            help='app list.',
        )
        # 是否删除整个目录
        parser.add_argument(
            '-d',
            '--directory',
            action='store_true',
            dest='directory',
            default=False,
            help='delete directory.',
        )

    def handle(self, *args, **options):
        print(options)
        try:

            if options['directory']:
                """
                删除目录
                """
                print('clear dir')
                try:
                    app_list = options['app']
                except Exception as e:
                    pass
                else:
                    if len(app_list) > 0:
                        print(app_list)
                    else:
                        print("all")

            else:
                """
                删除文件
                """
                print('clear file')
                try:
                    app_list = options['app']
                except Exception as e:
                    pass
                else:
                    if isinstance(app_list, list) and len(app_list) > 0:
                        print(app_list)
                    else:
                        print("all")
                        Public._meta.app_label
        except CommandError as e:
            self.stdout.write(self.style.ERROR('命令执行出错1'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('命令执行出错2'))
        else:
            self.stdout.write(self.style.SUCCESS('命令执行成功'))
