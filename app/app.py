import os 
import sys
import re

from kivy import *
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty

Builder.load_file('design.kv')

class CustomPopup(Popup):
	def __init__(self, **kwargs):
		super(Popup, self).__init__(**kwargs)
		self.dirname = ""
		self.filename = ""
		self.info = ""

	def _open(self, main):
		self.open()
		self.main_obj = main

	def _validate(self):
		self.dirname = self.ids._chapter.text.strip().lower()
		self.filename = self.ids._topic.text.strip().lower()
		self.info = self.ids._info.text.strip()
		if (not self.dirname or not self.filename or not self.info):
			err_btn = Button(text = "Input fields cannot be empty!!")
			err_pop = Popup(
				title = "ERROR",
				size_hint= (None, None),
				width = 320,
				height = 240,
				content = err_btn
			)
			err_btn.bind(on_press = err_pop.dismiss)
			err_pop.open()
			return
		else:
			pat = re.compile("^[a-z]{3,10}$")
			if (not pat.match(self.dirname) or not pat.match(self.filename)):
				self.ids.no_validate.text = "Invalid input for \n Chapter or Topic"
				return

		self.ids.no_validate.text = ""
		self.ids.add_button.disabled= False


	def _add(self):
		self.dismiss()
		self.ids._chapter.text = ""
		self.ids._topic.text = ""
		self.ids._info.text = ""
		self.ids.add_button.disabled= True
		self.data_storage()


	def data_storage(self):

		#list new directory name into dirs list
		dir_exst = False 
		with open("../data/dirs.txt","r+") as fp:
			for dirt in fp.readlines():
				if dirt[:-1] == self.dirname:
					dir_exst = True
			if not dir_exst:
				os.system(f"mkdir ../data/{self.dirname}")
				fp.write(self.dirname+'\n')
				btn = Button(
					text = self.dirname.upper(),
					size_hint_y = None,
					height = 50,
					on_press = self.main_obj.pressed_chapter
				)
				self.main_obj.ids.chapter_.add_widget(btn, index=1)
		fp.close()
		
		# list new filename into files list
		file_exst = False
		try:
			with open(f"../data/{self.dirname}/files.txt","r+") as fp:
				for file in fp.readlines():
					if file[:-1] == self.filename:
						file_exst = True
				if not file_exst:
					fp.write(self.filename+'\n')
			fp.close()
		except FileNotFoundError:
			with open(f"../data/{self.dirname}/files.txt","w") as fp:
				fp.write(self.filename+'\n')
			fp.close()

		# Create a new file and add data to it
		with open(f"../data/{self.dirname}/{self.filename}.txt","a") as fp:
			fp.write(self.info+'\n')
		fp.close()




class MyLayout(Widget):
	

	def __init__(self,**kwargs):
		super(MyLayout, self).__init__(**kwargs)
		self.add_chapters()
		self.pop = CustomPopup()

	def add_chapters(self):
		try:
			with open("../data/dirs.txt",'r') as fp:
				for line in fp.readlines():
					btn =  Button(
						text = line[:-1].upper(),
						size_hint_y = None,
						height = 50,
						on_press = self.pressed_chapter
					)
					self.ids.chapter_.add_widget(btn, index=1)
			fp.close()

		except FileNotFoundError:
			os.system("touch ../data/dirs.txt")

	def add_item_layer0(self):
		dataset = self.pop._open(self)

	def pressed_chapter(self, instance):
		self.dirname = instance.text.lower()

		self.ids.topic_.clear_widgets(children = None)

		with open(f"../data/{self.dirname}/files.txt",'r') as fp:
			for topic in fp.readlines():
				btn =  Button(
					text = topic[:-1].upper(),
					size_hint_y = None,
					height = 50,
					on_press = self.pressed_topic
				)
				self.ids.topic_.add_widget(btn, index=1)


	def pressed_topic(self, instance):
		filename = instance.text.lower()
		self.ids.info_.text = ""
		with open(f"../data/{self.dirname}/{filename}.txt") as fp:
			self.ids.info_.text = ''.join(fp.readlines())
		fp.close()
		self.dirname = ""
		

class LocalSearchApp(App):
	def build(self):
		return MyLayout()

if __name__ == "__main__":
	app = LocalSearchApp()
	app.run()

