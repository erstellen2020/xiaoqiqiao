"""
#泰克内部专用，version1.3版本
2020.7.019
更新：
忘记了，图片压缩有点问题还没有解决

待更新：
用户第一次登陆，得到用户的uid保存到本地，第二次后自动获取，节约跳转时间
断点续传
每一个h1 h2 需要暂停
"""

from selenium import webdriver
import time, os, re, markdown
from bs4 import BeautifulSoup
from PIL import Image
from selenium.webdriver.common.keys import Keys
import pyperclip


# 实验偏移量

class App:

    def __init__(self, user_name, user_key):
        """
        如果是打开浏览器显示是英文，请将如下信息取消注释，并删除下面定义的driver
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-CN'})
        self.driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
        """
        # 定义好驱动
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')
        # 标题层级，一个H标题为一层
        self.title_level = 0
        # 文本等级，一个普通文本或强调文本或者图片为一层
        self.text_level = 0
        # 标题等级，默认为一，此处判断是等级
        self.head_level = 1

        # xpath
        self.xpath = ''

        # expression
        self.expression = ''
        # 用户名
        self.user_name = user_name
        # 用户密码
        self.user_key = user_key

    def login(self):
        self.driver.get('https://login.xiaoqiqiao.com/login/login')
        # user_name
        self.driver.find_element_by_id("loginform-username").send_keys(self.user_name)
        # user_key
        self.driver.find_element_by_id("loginform-password").send_keys(self.user_key)
        # 登陆
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

                lab_edit = file.replace(".md", "")

        # 得到需要编辑实验的位置
        for i in range(len(title)):
            if title[i] == lab_edit:
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
        """修改分辨率为1024*768
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
        for i in range(2, self.head_level):
            time.sleep(0.5)
            self.driver.find_element_by_xpath(xpath).click()

    # 判断标题级别，自动点击
    def judge_head(self, expression):
        time.sleep(1.5)
        if 'h1' in expression:
            self.head_level = 1

        elif 'h3' in expression:
            self.head_level = 3

        elif 'h4' in expression:
            self.head_level = 4

        elif 'h5' in expression:
            self.head_level = 5

        expression = re.findall(r'<h[0-9]>(.*?)</h[0-9]>', expression)[0]
        if 'h1' in expression or 'h3' in expression or 'h4' in expression or 'h5' in expression:
            click = 'div:nth-child(1) > div:nth-child(1) > li'
            self.driver.find_element_by_css_selector(click).click()

        else:
            click = 'div:nth-child(1) > div:nth-child(2) > li'
            self.driver.find_element_by_css_selector(click).click()

        return expression

    # HTML常用的转义转化
    def html_transfer(self, expression):

        dict = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            'create1997pyj': ''
        }
        for key in dict:
            expression = expression.replace(key, dict[key])
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

    def chick_send(self):
        expression = str(self.expression)
        pyperclip.copy(expression)
        self.driver.find_element_by_xpath(self.xpath).send_keys(Keys.CONTROL, 'v')

    # 修补标题自带文本，防止插入图片时出现错误
    def head_label(self):
        # 标题的级别自增 1
        self.title_level += 1
        # 需要清空文本的级别数
        self.text_level = 0
        self.xpath = self.titile_item_xpath()
        # 输入内容
        self.chick_send()
        # 修补标题自带文本，防止插入图片时出现错误
        xpath = "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div[2]/div[3]/div/div[{}]/div/div[2]/div[" \
                "1]/div/div/div/div/img".format(self.title_level)
        self.driver.find_element_by_xpath(xpath).click()

    def judge_code(self):
        num1 = len(re.findall('ant-input code_textarea', self.driver.page_source))
        self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(4) > li").click()
        time1=time.time()
        while True:
            time2=time.time()
            num2 = len(re.findall('ant-input code_textarea', self.driver.page_source))
            if num2 - num1 == 1:
                break
            time.sleep(1.8)
            if time2-time1 > 5:
                self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(4) > li").click()


    def judge_text(self):
        num1 = len(re.findall('ant-input text_textarea', self.driver.page_source))
        self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(1) > li").click()
        time1=time.time()
        while True:
            time2 = time.time()
            num2 = len(re.findall('ant-input text_textarea', self.driver.page_source))
            if num2 - num1 == 1:
                break
            time.sleep(1.8)
            if time2 - time1 > 5:
                self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(1) > li").click()

    def judge_title(self,click):
        self.driver.find_element_by_css_selector(click).click()
        num1 = len(re.findall('ant-input title_textarea', self.driver.page_source))
        while True:
            num2 = len(re.findall('ant-input title_textarea', self.driver.page_source))
            if num2 - num1 == 1:
                break
            # else:
            #     self.driver.find_element_by_css_selector(click).click()
            time.sleep(1.5)

    def judge_img(self):
        while True:
            flag_img = self.driver.page_source
            if 'type="file"' in flag_img:
                break
            time.sleep(1.5)
    # 解析
    def md_analysis(self, expression):
        # 得到代码
        if '<p><code>' in expression:
            self.expression = re.sub(r'<p><code>.*\n', '', expression).replace("</code></p>", "")
            # 点击文本

            self.judge_code()
            self.text_level += 1
            self.xpath = self.text_item_xpath()
            self.chick_send()

        # 得到H标签1
        elif '<h1>' in expression or '<h2>' in expression or '<h3>' in expression or '<h4>' in expression or '<h5>' in expression:
            self.expression = self.judge_head(expression)
            self.head_label()
            self.head_item_click()

        # 得到图片
        elif 'img' in expression:
            expression = re.findall(r'src="(.*?)"/', expression)[0]
            expression = os.path.abspath(expression)
            self.driver.find_element_by_css_selector("div:nth-child(2) > div:nth-child(3) > li").click()
            expression = self.compress_image(expression)
            self.judge_img()
            # 自增1
            self.text_level += 1
            self.driver.find_element_by_css_selector('input[type="file"]').send_keys(expression)
            while True:
                flag_img = self.driver.page_source
                if 'type="file"' in flag_img:
                    time.sleep(1.5)
                else:
                    break


        elif '<p>' in expression:
            if 'strong' in expression:
                self.expression = expression.replace("<p><strong>", "").replace("</strong></p>", "")
            else:
                self.expression = expression.replace("<p>", '').replace("</p>", "")
                # 点击文本
            self.judge_text()
            self.text_level += 1
            self.xpath = self.text_item_xpath()
            self.chick_send()

    def open_file(self):
        self.add_md5()
        with open('new.md', "r", encoding='UTF-8') as f:
            html = markdown.markdown(f.read())
            soup = BeautifulSoup(html, "html.parser")
            for line in soup:
                if line != '\n':
                    line = self.html_transfer(str(line))
                    self.md_analysis(line)
            # 保存
            self.driver.find_element_by_xpath(
                "//div[@id='rootWrapper']/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/button[2]").click()

    def rm_temp(self):
        for files in os.listdir("."):
            if "new" in files:
                os.remove(files)


if __name__ == '__main__':
    a = App('user', 'pwd')
    a.login()
    a.lab_edit()
    a.clean_lab()
    a.open_file()
    a.rm_temp()
