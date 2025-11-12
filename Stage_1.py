import argparse
import urllib.request
import re

class CLI_Ubuntu:
    def __init__(self):
        self.params = self.cmd_line()
        self.print_args()
        self.Ubuntu_packages()

    def cmd_line(self):
        params = {}
        parser = argparse.ArgumentParser(description="CLI") #объявление объекта

        parser.add_argument('--package-name', '-p',
                               type=str,
                               required=True,
                               help="name of package"
                               )

        parser.add_argument('--url', '-u',
                                type=str,
                                required=True,
                                help="url of package"
                                )

        parser.add_argument('--graph-name', '-g',
                                type=str,
                                default='graph.png',
                                help="name of graph file"
                                )
        try:
            args = parser.parse_args()
            #print(args)
            params['package_name'] = args.package_name
            params['url'] = args.url
            params['graph_name'] = args.graph_name
            #print(params)
            return params

        except SystemExit:
            print(f"Ошибка при вводе параметров")
            exit(-1)



    def print_args(self):
        print(f"package-name:\t{self.params['package_name']}")
        print(f"url:\t\thttps://packages.ubuntu.com/{self.params['url']}")
        print(f"graph_name:\t{self.params['graph_name']}")
    
    def Ubuntu_packages(self):
        url =  f"https://packages.ubuntu.com/{self.params['url']}/{self.params['package_name']}"
        print(f"https://packages.ubuntu.com/{self.params['url']}/{self.params['package_name']}")

        file = urllib.request.urlopen(url)
        new_file = file.read()

        error_found = b'<h1>Error</h1>' #регулярка в битовый
        reg = re.search(error_found, new_file)
        if reg != None:
            print(f"Неккоректная ссылка")
        else:

            flag_stop = 0
            find_uldep = b'<ul class="uldep">'
            this_file = new_file
            uldep_parts = this_file.split(find_uldep, -1) #разделение по регулярному выражению
            find_ulrec = b'<ul class="ulrec">' #проверка на наличие рекомендаций
            check = re.search(find_ulrec, uldep_parts[2])
            if check != None:
                uldep_parts_found = uldep_parts[2].split(find_ulrec, -1)
                check_uldep = 0
                flag_stop = 1
            else:
                check_uldep = 1
                # В uldep_parts_found[0] хранятся нужные пакеты

            if flag_stop == 0:
                find_ulsug = b'<ul class="ulsug">'
                check = re.search(find_ulsug, uldep_parts[2])
                if check != None:
                    uldep_parts_found = uldep_parts[2].split(find_ulsug, -1)
                    check_uldep = 0
                    flag_stop = 1
                else:
                    check_uldep = 1

            if flag_stop == 0:
                find_ulenh = b'<ul class="ulenh">'
                check = re.search(find_ulenh, uldep_parts[2])
                if check != None:
                    uldep_parts_found = uldep_parts[2].split(find_ulenh, -1)
                    check_uldep = 0
                    flag_stop = 1
                else:
                    check_uldep = 1
                    # В uldep_parts_found[0] хранятся пакеты необходимые для работы вводимого пакета

            pattern = (b'>([a-zA-Z0-9_\\-\\+]*)</a>\n\t')
            reg = re.compile(pattern)
            if check_uldep == 0:
                package = reg.findall(uldep_parts_found[0])
            else:
                package = reg.findall(uldep_parts[2])
            i = 0
            package_str = set()
            while i < len(package):
                package_str.add(str(package[i], encoding='utf-8'))
                i = i + 1
            print('Зависимые пакеты:', package_str)

print("Package for example: aide/abyss \nURL format: questing")
CLI = CLI_Ubuntu()
