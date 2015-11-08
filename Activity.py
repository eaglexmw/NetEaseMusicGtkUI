# coding=utf-8

import pygtk
import gtk
import NetEase
import Utility

pygtk.require20()


class MainActivity(gtk.Window):
    def __init__(self):
        super(MainActivity, self).__init__()

        self.container = gtk.VBox(False, 0)
        self.add(self.container)

        self.btn_login = gtk.Button("Login")
        self.btn_login.set_size_request(200, 30)
        self.btn_login.connect("clicked", self.login_dialog)
        self.container.pack_start(self.btn_login, True, True, 0)

        self.connect("delete_event", self.delete_event)
        self.show_all()

        self.net_ease = NetEase.get_instance()

    def login_dialog(self, widget, data=None):
        dialog = LoginDialog()
        dialog.show()
        self.show()

    def delete_event(self, widget, data=None):
        gtk.main_quit()
        return False

    def main(self):
        gtk.main()


class LoginDialog(gtk.Dialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        self.set_title("登陆框")

        container = gtk.HBox()
        self.vbox.pack_start(container)

        input_vbox = gtk.VBox()
        container.pack_start(input_vbox)

        self.input_name = gtk.Entry(36)
        self.input_name.set_size_request(200, 60)
        input_vbox.pack_start(self.input_name)

        self.input_passwd = gtk.Entry(36)
        self.input_passwd.set_size_request(200, 60)
        self.input_passwd.set_visibility(False)
        input_vbox.pack_start(self.input_passwd)

        login_btn_vbox = gtk.VBox()
        container.pack_end(login_btn_vbox)

        btn_login = gtk.Button("Login")
        btn_login.set_size_request(80, 100)
        btn_login.connect("clicked", self.login)
        login_btn_vbox.pack_end(btn_login, False)

        self.show_all()

        self.net_ease = NetEase.get_instance()

    def login(self, widget, data=None):
        user_name = self.input_name.get_text()
        password = self.input_passwd.get_text()
        if user_name == "" or password == "":
            Utility.toast("用户名或密码不能为空")
            return
        login_data = self.net_ease.login(user_name, Utility.md5(password))

        if not login_data:
            Utility.toast("登录失败")
            return

        self.do_close(self)

if __name__ == "__main__":
    mainActivity = MainActivity()
    mainActivity.main()
