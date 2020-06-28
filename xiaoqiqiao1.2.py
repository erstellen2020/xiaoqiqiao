"""
#泰克内部专用，version1.2版本
2020.6.29
更新：
(1)自动压缩图片，超过500kb自动压缩
(2)支持强调文本
联系人：pengyongjian@tech-lab.cn
本项目由广州许国军、胡英铭等广州教学部老师大力支持
后续版本敬请期待
"""

from selenium import webdriver
import time, os, re, markdown
from bs4 import BeautifulSoup
from PIL import Image


# 实验偏移量

class App():

    def __init__(self):
        self.title_level = 0
        self.text_level = 0
        self.head_level = 1

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-CN'})
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://login.xiaoqiqiao.com/login/login')
        user_name = "账户名"
        user_key = "密码"

        # username
        self.driver.find_element_by_id("loginform-username").send_keys(user_name)

        # userkey
        self.driver.find_element_by_id("loginform-password").send_keys(user_key)
        self.driver.find_element_by_xpath(u"//input[@value='登录']").click()
        time.sleep(5)

    def lab_edit(self):
        offset = 0
        # lab
        # 拿到用户id，得到实验编辑链接
        lab_url = str(self.driver.current_url).replace('Course', 'EditExperiment/LabManual')
        # 进入编辑实验
        self.driver.get(lab_url)
        time.sleep(3)

        # 编辑实验列表
        self.driver.find_element_by_css_selector(" div.lab_navbar > ul > li:nth-child(2)").click()

        time.sleep(3)
        # 获取全部实验标题
        title = self.driver.find_element_by_css_selector("#itemContainer").text
        title = title.replace(" 编辑复制上线测试清理环境删除", "").split("\n")

        # 获取当前需要上传的文件名称
        for file in os.listdir("."):
            if '.md' in file and not 'new' in file:
                self.file = file
                print(file)
                lab_edit = file.replace(".md", "")

        # 得到需要编辑实验的位置
        for i in range(len(title)):
            if (title[i] == lab_edit):
                offset = i + 1

        # 点击编辑
        self.driver.find_element_by_css_selector(
            "#itemContainer > tr:nth-child(" + str(offset) + ") > th:nth-child(2) > span.obtained.edit_test").click()
        # 点击实验步骤
        self.driver.find_element_by_css_selector("div.basic_navbar > ul > li:nth-child(2)").click()

    def clean_lab(self):
        step_all = (re.findall('id="([step_]+[0-9].*?)\"', self.driver.page_source))
        for step in step_all:
            xpath = ' //*[@id="' + step + '"]/div[1]/div[1]/ul/li[2]/img'
            time.sleep(0.25)
            self.driver.find_element_by_xpath(xpath).click()
            time.sleep(0.25)
            self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]/button[1]").click()

    # 标题的描述，传入标题层数，自动返回此标题的full_xpath
    def titile_item_xpath(self):
        return "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[1]/textarea".format(
            self.title_level)

    # 文本描述，传入标题层数，以及当前编辑的文本，自动返回当前文本的full_xpath
    def text_item_xpath(self):
        return "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[2]/div[" \
               "1]/div/div[{}]/div/div/textarea".format(self.title_level, self.text_level)

    # 图片描述，传入标题层数，以及当前编辑的图片，自动返回当前图片的full_xpath
    def image_item_xpath(self):
        return "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[2]/div[" \
               "1]/div/div[{}]/div/div/div/div/input".format(self.title_level, self.text_level)

    def get_size(self, file):
        # 获取文件大小:KB
        size = os.path.getsize(file)
        return size / 1024

    # 压缩图片，将图片压缩至500kb以下
    def compress_image(self, infile, limit_size=500) -> str:
        outfile = 'new_' + infile
        """不改变图片尺寸压缩到指定大小
        :param infile: 压缩源文件
        :param outfile: 压缩文件保存地址 此处使用自动保存为新地址，源图片前缀 new_
        :param limit_size: 压缩目标，KB
        :return: 压缩文件地址
        """
        o_size = self.get_size(infile)
        if o_size <= limit_size:
            return infile
        outfile = os.path.join(os.getcwd(), 'new_' + str(infile.split('\\')[-1]))
        # 此处只压缩一次，基本满足要求
        if o_size >= limit_size:
            im = Image.open(infile)
            im = im.resize((1024, 768), Image.ANTIALIAS)
            im.save(outfile, colors=255)
        return outfile

    # 通过点击改变标题的级别,当前默认为1
    def head_item_click(self):
        xpath = "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[1]/div[" \
                "1]/ul/li[1]/img".format(self.title_level)
        for i in range(1, self.head_level):
            time.sleep(0.5)
            self.driver.find_element_by_xpath(xpath).click()

    # 修补标题自带文本，防止插入图片时出现错误
    def patch(self):
        xpath = "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[2]/div[" \
                "1]/div/div/div/div/img".format(self.title_level)
        self.driver.find_element_by_xpath(xpath).click()

    # 判断标题级别，自动点击
    def judge_head(self, expression):
        if 'h1' in expression:
            expression = re.findall("<h1>(.*?)</h1>", expression)
            self.head_level = 1


        elif 'h3' in expression:
            expression = re.findall("<h3>(.*?)</h3>", expression)
            self.head_level = 3

        elif 'h4' in expression:
            expression = re.findall("<h4>(.*?)</h4>", expression)
            self.head_level = 4

        elif 'h5' in expression:
            expression = re.findall("<h5>(.*?)</h5>", expression)
            self.head_level = 5

        return expression

    # HTML常用的转义转化
    def html_transfer(self, expression):

        dict = {
            '&lt;':'<',
            '&gt;':'>',
            '&amp;':'&',
            '&quot;':'"',
            'create1997pyj':''
        }
        for key in dict:
            expression = expression.replace(key,dict[key])
        return expression

    def add_md5(self):
        code = False
        with open(self.file, 'r', encoding='utf-8') as file1:
            with open('new.md', 'w+', encoding='utf-8') as file2:
                for line in file1.readlines():
                    if '```' in line:
                        code = not code
                    if re.findall(r'^ *$', line) and code:
                        line = 'create1997pyj' + '\n'
                    if re.findall(r'^#', line) and code:
                        line = 'create1997pyj' + line
                    file2.write(line)

    # 解析
    def md_analysis(self, expression):
        # 得到代码
        if '<p><code>' in expression:
            # expression = expression.replace("<p><code>shell", "").replace("</code></p>", "").strip('\n')
            expression = re.sub(r'<p><code>.*\n','',expression).replace("</code></p>", "")
            # 点击文本

            self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(4) > li").click()
            self.text_level = self.text_level + 1
            xpath = self.text_item_xpath()
            self.driver.find_element_by_xpath(xpath).send_keys(expression)

        # 得到H2
        elif 'h2' in expression:
            self.head_item_click()
            expression = re.findall("<h2>(.*?)</h2>", expression)
            # 添加H2
            self.driver.find_element_by_css_selector("div:nth-child(1) > div:nth-child(2) > li").click()
            # 标题的级别自增 1
            self.title_level = self.title_level + 1
            # 需要清空文本的级别数
            self.text_level = 0
            xpath = self.titile_item_xpath()
            # 输入内容
            self.driver.find_element_by_xpath(xpath).send_keys(expression)
            # 删除自带文本
            self.patch()

        # 得到H1
        elif 'h1' in expression or 'h3' in expression or 'h4' in expression or 'h5' in expression:
            self.driver.find_element_by_css_selector("div:nth-child(1) > div:nth-child(1) > li").click()
            # 判断自己属于第几层标题
            expression = self.judge_head(expression)
            # 标题的级别自增 1
            self.title_level = self.title_level + 1
            # 需要清空文本的级别数
            self.text_level = 0
            xpath = self.titile_item_xpath()
            # 输入内容
            self.driver.find_element_by_xpath(xpath).send_keys(expression)
            time.sleep(0.5)
            # 删除文本
            self.patch()
            self.head_item_click()


        # 得到图片
        elif 'img' in expression:
            expression = re.findall(r'src="(.*?)"/', expression)[0]

            expression = os.path.abspath(expression)
            self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(3) > li").click()
            print("------------IMG----------")
            expression = self.compress_image(expression)

            # 自增1
            self.text_level = self.text_level + 1
            self.driver.find_element_by_css_selector('input[type="file"]').send_keys(expression)
            time.sleep(1)
        # # 得到强调文本
        elif 'strong' in expression:
            print(expression)
            expression = expression.replace("<p><strong>", "").replace("</strong></p>", "")
            print(expression)
            print("------------STRONG----------")
            self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(2) > li").click()
            self.text_level = self.text_level + 1
            xpath = self.text_item_xpath()
            self.driver.find_element_by_xpath(xpath).send_keys(expression)
        # 得到普通文本
        elif 'p' in expression:
            expression = expression.replace("<p>", '').replace("</p>", "")
            # 点击文本
            self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(1) > li").click()
            self.text_level = self.text_level + 1
            xpath = self.text_item_xpath()
            self.driver.find_element_by_xpath(xpath).send_keys(expression)
            time.sleep(0.5)

    def open_file(self):
        self.add_md5()
        with open('new.md', "r", encoding='UTF-8') as f:
            html = markdown.markdown(f.read())
            soup = BeautifulSoup(html, "html.parser")
            for line in soup:
                time.sleep(1)
                line =self.html_transfer(str(line))
                self.md_analysis(str(line))
            # 保存
            self.driver.find_element_by_xpath(
                "//div[@id='rootWrapper']/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/button[2]").click()

    def rm_temp(self):
        for files in os.listdir("."):
            if "new" in files:
                os.remove(files)


if __name__ == '__main__':
    a = App()
    a.login()
    a.lab_edit()
    a.clean_lab()
    a.open_file()
    a.rm_temp()
