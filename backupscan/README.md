## 需要的库：

```
threading
requests
python-hashes
```

python-hashes在该文件中附带。只需下载头两个库就行了



## 使用说明

```
Usage:
      _                      _                              ____
     | |__     __ _    ___  | | __  _   _   _ __           / ___|    ___    __ _   _ __
     | '_ \   / _` |  / __| | |/ / | | | | | '_ \   _____  \___ \   / __|  / _` | | '_ \
     | |_) | | (_| | | (__  |   <  | |_| | | |_) | |_____|  ___) | | (__  | (_| | | | | |
     |_.__/   \__,_|  \___| |_|\_\  \__,_| | .__/          |____/   \___|  \__,_| |_| |_|
                                           |_|


Options:
  -h, --help            show this help message and exit
  -u TARGET_URL, --url=TARGET_URL
                        single url
  -L URL_LIST, --list=URL_LIST
                        url list file
  -t THREAD             thread number
  -o OUTFILE            output file
  --timeout=TIMEOUT     timeout count
  --title               Get domain's title
```

必须参数-u 或者-L，指定一个url或者一个url文件(一行一个url)。不加其他参数时会去扫描一些敏感文件，可以自己往里面加字典或者自己改代码，从字典文件里读都行【有空加上该功能】

--title，扫描url对应网页的标题，方便找寻有价值的网页进行渗透测试。默认结果输出文件为results-domains.txt，且只保存有标题的url

-t，线程数，默认为5

使用了simhash来判断404页面，所以可能会慢一点。



##  待完成

- [ ] 还有一个报错为解决，但是不影响正常使用，回在扫描时导致部分url扫描不到

- [ ] 指定从文件读取扫描字典