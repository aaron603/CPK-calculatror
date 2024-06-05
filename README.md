"该程序为按照深科技Mes系统导出的RRU测试数据的csv文件，按照测试项目分别生成cpk，以供研发分析之用，可以按照导出csv数据文件，逐一分析cpk。\n"
            "1）“选择csv文件”浏览框，点击右侧“浏览”，选在深科技mes系统导出需要分析测试工位的数据源文件；\n"
            "2）“拆分csv文件”按钮作用：选择测试数据所在csv文件后，点击此按钮开始按照模块为单位拆分测试数据，并自动保存为一个单独目录split_files。测试fail的模块文件命名末尾会自动增加fail，用户如果不想这些失败模块数据参与cpk运算，可以在文件拆分后cpk计算前，手动删除这些失败的模块数据，以避免其参与运算；\n"
            "3）“生成配置文件”按钮作用，点击此按钮后，会自动在用户选择目录下生成一个配置文件，用户可以根据需要，把需要参与计算cpk的测试项目，对应测试项目配置为True并保存，默认值全部为False；\n"
            "4）“提取测试项数据”按钮作用，点击此按钮后，用户选择根据程序提示选择拆分后RRU模块测试数据所在目录，程序会自动将该目录下的模块数据按照测试项目为单位进行提取，生成便于cpk计算的测试项目为单位的文件，保存在test_data文件夹下；\n"
            "5）“计算CPK”按钮作用，点击此按钮后，用户需要先根据提示选择计算cpk的配置文件（注意需要计算cpk的测试项目，用户需要先在配置文件修改为True）；选择完成配置文件后，程序会提示继续选择计算cpk文件所在的提取数据目录，然后程序会自动开始计算cpk（程序会自动跳过测试项目为fail的值，fail结果不参与cpk计算），并画cpk正态分布图保存在cpk_plots目录，并会生成日志，自动保存在cpk_results结果目录中。"
