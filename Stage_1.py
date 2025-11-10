import argparse

class CLI_Ubuntu:
    def __init__(self):
        self.params = self.cmd_line()
        self.print_args()


    def cmd_line(self):
        params = {}
        #try:
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
        print(f"url:\t\t{self.params['url']}")
        print(f"graph_name:\t{self.params['graph_name']}")


CLI = CLI_Ubuntu()
