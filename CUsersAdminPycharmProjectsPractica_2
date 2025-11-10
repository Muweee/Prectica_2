import argparse

  class CLI_Ubuntu:
      def __init__(self):
          self.params = self.cmd_line()
          self.print_args()


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

          parser.add_argument('--ascii', '-as',
                                                          type=bool,
                                                          default=False,
                                                          help="name of graph file"
                                                          )


          parser.add_argument('--max-depth', '-d',
                                                          type=int,
                                                          default=5,
                                                          help="name of graph file"
                                                          )


          parser.add_argument('--filter', '-f',
                                                          type=str,
                                                          default='',
                                                          help="name of graph file"
                                                          )

          args = parser.parse_args()
        # print(args)

          params['package_name'] = args.package_name
          params['url'] = args.url
          params['graph_name'] = args.graph_name
          params['ascii'] = args.ascii
          params['max_depth'] = args.max_depth
          params['filter'] = args.filter
          return params

          def print_args(self):
             print(f"package-name:\t{self.params['package_name']}")
             print(f"url:\t\t{self.params['url']}")
             print(f"graph_name:\t{self.params['graph_name']}")
             print(f"ascii:\t\t{self.params['ascii']}")
             print(f"max_depth:\t{self.params['max_depth']}")
             print(f"filter:\t{self.params['filter']}")


        CLI = CLI_Ubuntu()
