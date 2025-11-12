import argparse
import urllib.request
import re

class CLI_Ubuntu:
    def __init__(self):
        self.params = self.cmd_line()
        self.graph = {}
        self.visited = set()
        self.recursion_stack = set()
        self.cycles = []

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
                            default='graph.png',
                            help="name of graph file"
                            )

        parser.add_argument('--test-mode', '-t',
                            action='store_true',
                            help="enable test mode"
                            )

        parser.add_argument('--test-file', '-f',
                            type=str,
                            help="path to test file with graph description"
                            )

        parser.add_argument('--reverse-deps', '-r',
                            type=str,
                            required=True,
                            help="show reverse dependencies for the given package"
                            )

        try:
            args = parser.parse_args()
            params['package_name'] = args.package_name
            params['url'] = args.url
            params['graph_name'] = args.graph_name
            params['test_mode'] = args.test_mode
            params['test_file'] = args.test_file
            params['reverse_deps'] = args.reverse_deps
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

    def bfs_recursive(self, start_package, current_depth_recursive=0, max_depth_recursive=15):
        if current_depth_recursive >= max_depth_recursive:
            return

        if start_package in self.visited:
            return

        if start_package in self.recursion_stack:
            self.cycles.append(start_package)
            return

        self.visited.add(start_package)
        self.recursion_stack.add(start_package)

        dependencies = self.get_dependencies(start_package) #добываем зависимости нашего пакета
        self.graph[start_package] = dependencies #первый элемент графа с разетвлением

        #смотрим зависимости зависимых пакетов
        for obj in dependencies:
            self.bfs_recursive(obj, current_depth_recursive + 1, max_depth_recursive)

        self.recursion_stack.remove(start_package)

    def detect_cycles(self):
        self.visited.clear()
        self.recursion_stack.clear()
        self.cycles.clear()

        all_keys = set(self.graph.keys())
        for key in all_keys:
            if key not in self.visited:
                self.cycle_detection_dfs(key)

        return len(self.cycles) > 0

    def cycle_detection_dfs(self, key):
        if key in self.recursion_stack: #вернулись к нему
            self.cycles.append(key)
            return

        if key in self.visited: #уже посещали
            return

        self.visited.add(key)
        self.recursion_stack.add(key)

        if key in self.graph:
            for dep in self.graph[key]:
                if dep in self.graph:  #если зависимость есть в графе
                    self.cycle_detection_dfs(dep)
                else:
                    #если зависимости нет в графе
                    if dep not in self.visited:
                        self.graph[dep] = self.get_dependencies(dep)
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
    def get_reverse_dependencies(self, current_package):
        reverse_deps = set()
        for package, deps in self.graph.items():
            if current_package in deps:
                reverse_deps.add(package)
        return reverse_deps

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

        self.bfs_recursive(start_package)

        self.detect_cycles()

        self.print_graph()
        self.print_cycles()

        transitive_deps = self.get_transitive_dependencies(start_package)
        print(f"\nТранзитивные зависимости для {start_package}: {', '.join(transitive_deps)}")

        if self.params['reverse_deps']:
            reverse_deps = self.get_reverse_dependencies(self.params['reverse_deps'])
            if reverse_deps:
                print(f"\nОбратные зависимости для {self.params['reverse_deps']}: {', '.join(reverse_deps)}")
            else:
                print(f"\nОбратные зависимости для {self.params['reverse_deps']}: не найдены")

        #print(f"\nВсего пакетов в графе: {len(self.graph)}")

if __name__ == "__main__":
    print("\nПакеты для примера: aide/abyss \nURL формат: questing")
    print ("Строка для Ubuntu формата: python Stage_1.py -p aide -u questing")
    print("\nФайлы для тестового режима: test_cycles.txt, test.txt")
    print("Строка для тестового режима:python Stage_1.py -p A -u foo -t -f test.txt")
    print("Строка для режима обратных зависимостей: python Stage_1.py -p A -u foo -t -f test_4.txt -r D")
    print("Файлы для работы с зависимостями: test_4.txt")

    CLI = CLI_Ubuntu()
    CLI.run()

