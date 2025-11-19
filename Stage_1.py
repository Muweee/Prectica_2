import argparse
import urllib.request
import re
from collections import deque
import plantuml
import requests


class CLI_Ubuntu:
    def __init__(self):
        self.params = self.cmd_line()
        self.graph = {}
        self.visited = set()
        self.recursion_stack = set()
        self.cycles = []
        self.reverse_deps = set()

    def cmd_line(self):
        params = {}
        parser = argparse.ArgumentParser(description="CLI")
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
                            default='graph.svg',
                            help="name of graph svg file"
                            )

        parser.add_argument('--test-mode', '-t',
                            action='store_true',
                            help="enable test mode"
                            )

        parser.add_argument('--test-file', '-f',
                            type=str,
                            help="path to test file with graph description"
                            )
        
        """parser.add_argument('--reverse-deps', '-r',
                            type=str,
                            required=True,
                            help="show reverse dependencies for the given package"
                            )"""
        
        try:
            args = parser.parse_args()
            params['package_name'] = args.package_name
            params['url'] = args.url
            params['graph_name'] = args.graph_name
            params['test_mode'] = args.test_mode
            params['test_file'] = args.test_file
            #params['reverse_deps'] = args.reverse_deps
            return params

        except SystemExit:
            print(f"Ошибка при вводе параметров")
            exit(-1)

    def print_args(self):
        print(f"package-name:\t{self.params['package_name']}")
        print(f"url:\t\t{self.params['url']}")
        print(f"graph_name:\t{self.params['graph_name']}")
        print(f"test_mode:\t{self.params['test_mode']}")
        if self.params['test_mode']:
            print(f"test_file:\t{self.params['test_file']}")

    def get_dependencies_from_file(self, package_name, file_):
        lines = file_.strip().split('\n')

        for line in lines:
            if ':' in line:
                package, deps = line.split(':', 1)
                if package.strip() == package_name:
                    deps = [dep.strip() for dep in deps.strip().split(',') if dep.strip()]
                    return deps
        return []

    def get_dependencies_from_Ubuntu(self, package_name):
        url = f"https://packages.ubuntu.com/{self.params['url']}/{package_name}"
        print(f"Запрашиваем: {url}")

        try:
            file = urllib.request.urlopen(url)
            new_file = file.read()
        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")
            return []

        error_found = b'<h1>Error</h1>'
        reg = re.search(error_found, new_file)
        if reg != None:
            print(f"Некорректная ссылка для пакета {package_name}")
            return []

        flag_stop = 0
        find_uldep = b'<ul class="uldep">'
        this_file = new_file
        uldep_parts = this_file.split(find_uldep, -1)

        if len(uldep_parts) > 2:
            find_ulrec = b'<ul class="ulrec">'
            check = re.search(find_ulrec, uldep_parts[2])
            if check != None:
                uldep_parts_found = uldep_parts[2].split(find_ulrec, -1)
                check_uldep = 0
                flag_stop = 1
            else:
                check_uldep = 1

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

            pattern = (b'>([a-zA-Z0-9_\\-\\+]*)</a>\n\t')
            reg = re.compile(pattern)
            if check_uldep == 0: #and 'uldep_parts_found' in locals():
                package = reg.findall(uldep_parts_found[0])
            else:
                package = reg.findall(uldep_parts[2])

            i = 0
            package_str = set()
            while i < len(package):
                package_str.add(str(package[i], encoding='utf-8'))
                i = i + 1
            return list(package_str)
        return []

    def get_dependencies(self, package_name):
        if self.params['test_mode'] and self.params['test_file']:
            with open(self.params['test_file'], 'r', encoding='utf-8') as f:
                file_ = f.read()
            return self.get_dependencies_from_file(package_name, file_)
        else:
            return self.get_dependencies_from_Ubuntu(package_name)

    def bfs_recursive(self, q):
            if not q:
                return

            start_package = q.popleft()
            
            if start_package not in self.visited:
                self.visited.add(start_package)
                
                dependencies = self.get_dependencies(start_package)  # добываем зависимости нашего пакета
                self.graph[start_package] = dependencies  # первый элемент графа с разетвлением
                
                # добавляем в очередь зависимые пакеты
                for obj in dependencies:
                    if obj not in self.visited:
                        q.append(obj)

            self.bfs_recursive(q)

    def detect_cycles(self):
        self.visited.clear()

        all_keys = set(self.graph.keys())
        for key in all_keys:
            if key not in self.visited:
                self.cycle_detection_dfs(key)

        return len(self.cycles) > 0

    def cycle_detection_dfs(self, key):
        if key in self.recursion_stack: #вернулись к узлу -> нашли цикл
            self.cycles.append(key)
            return

        if key in self.visited: #уже посещали и рассматривали
            return

        self.visited.add(key)
        self.recursion_stack.add(key)

        for dep in self.graph[key]:
            if dep in self.graph:  #если зависимость есть в ключах графа
                self.cycle_detection_dfs(dep)

        self.recursion_stack.remove(key)

    def get_transitive_dependencies(self, package):
        visited = set()
        result = set()

        def dfs(current_package):
            if current_package in visited:
                return
            visited.add(current_package)

            if current_package in self.graph:
                for dep in self.graph[current_package]:
                    result.add(dep)
                    dfs(dep)

        dfs(package)
        return result

    def get_reverse_dependencies(self, current_package, current_deep = 0, max_deep = 4):
        if current_deep >= max_deep:
            return
        if current_package in self.cycles:
            return
        for package, deps in self.graph.items():
            if current_package in deps:
                self.reverse_deps.add(package)
                self.get_reverse_dependencies(package, current_deep + 1, max_deep)
        return self.reverse_deps

    def generate_plantum(self):
        lines = ["@startuml"]
        for package, deps in self.graph.items():
            for dep in deps:
                lines.append(f' "{package}" -> "{dep}"')
        lines.append("@enduml")
        return "\n".join(lines)

    def save_plantuml_to_svg(self):

        try:
            # Генерируем PlantUML текст
            plantuml_text = self.generate_plantum()
            print("\n==== PlantUML код ====")
            print(plantuml_text)

            # Используем публичный сервер PlantUML
            encode_text = plantuml.deflate_and_encode(plantuml_text)

            server_url = f"http://www.plantuml.com/plantuml/svg/{encode_text}"

            print(f"Запрашиваем SVG с: {server_url}")

            #Делаем запрос к серверу PlantUML
            response = requests.get(server_url, timeout=30)
            #Сохраняем в файл
            output_file = self.params['graph_name']
            if not output_file.endswith('.svg'):
                output_file += '.svg'

            if response.status_code == 200 and 'svg' in response.headers.get('Content-Type'):
                #Получаем чистый SVG код
                svg_content = response.text

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(svg_content)

                print(f"\nГраф успешно сохранен в файл: {output_file}")
                print(f"Размер SVG файла: {len(svg_content)} байт")
            else:
                print("\nОшибка: Не удалось сгенерировать SVG через PlantUML")

        except Exception as e:
            print(f"\nОшибка при сохранении SVG: {e}")

    def save_svg(self):
        uml_code = self.generate_plantum()
        with open("graph.svg","w",encoding="utf-8") as f:
            f.write(uml_code)

    def print_graph(self):
        print("\n==== Граф зависимостей ====")
        for key_package, deps in self.graph.items():
            if deps:
                print(f"{key_package} -> {', '.join(deps)}")
            else:
                print(f"{key_package} -> []")

    def print_cycles(self):
        if self.cycles:
            print(f"\nНайдены циклические зависимости для пакетов: {', '.join(set(self.cycles))}")
        else:
            print("\nЦиклических зависимостей не найдено")

    def run(self):
        print(f"Режим тестирования: {self.params['test_mode']}")

        if self.params['test_mode']:
            print(f"Тестовый файл: {self.params['test_file']}")

        start_package = self.params['package_name']
        print(f"Граф зависимостей для пакета: {start_package}")

        q = deque()
        q.append(start_package)
        self.bfs_recursive(q)  # теперь есть граф и посещенные

        self.detect_cycles() #в поисках циклов

        self.print_graph()
        self.print_cycles()

        transitive_deps = self.get_transitive_dependencies(start_package)
        print(f"\nТранзитивные зависимости для {start_package}: {', '.join(transitive_deps)}")
        
        
        # if self.params['reverse_deps']:
        #     reverse_deps = self.get_reverse_dependencies(self.params['reverse_deps'])
        #     if reverse_deps:
        #         print(f"\nОбратные зависимости для {self.params['reverse_deps']}: {', '.join(reverse_deps)}")
        #     else:
        #         print(f"\nОбратные зависимости для {self.params['reverse_deps']}: не найдены")

        # self.save_svg()
        self.save_plantuml_to_svg()
        #print(f"\nВсего пакетов в графе: {len(self.graph)}")

if __name__ == "__main__":
    print("\nПакеты для примера: aide/abyss \nURL формат: questing")
    print ("Строка для Ubuntu формата: python Stage_1.py -p aide -u questing")
    print("\nФайлы для тестового режима: test_cycles.txt, test.txt")
    print("Строка для тестового режима:python Stage_1.py -p A -u foo -t -f test.txt")
    print("Строка для режима обратных зависимостей: python Stage_1.py -p A -u foo -t -f test_4.txt -r D")
    print("python Stage_1.py -p aide -u questing -r gcc-15-base")
    print("Файлы для работы с зависимостями: test_4.txt")
    
    CLI = CLI_Ubuntu()
    CLI.run()

