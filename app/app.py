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
		self.content_0 = ""
		self.content_1 = ""
		self.content_2 = ""

	def _open(self, main):
		self.open()
		self.main_obj = main

	def _validate(self):
		self.content_0 = self.ids.content_layer0.text
		self.content_1 = self.ids.content_layer1.text
		self.content_2 = self.ids.content_layer2.text
		if (not self.content_0 or not self.content_1 or not self.content_2):
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
			pat = re.compile("^[a-zA-Z]{3,10}$")
			if (not pat.match(self.content_0) or not pat.match(self.content_1)):
				self.ids.no_validate.text = "Invalid input in \n layer0 or layer1"
				return

		self.ids.no_validate.text = ""
		self.ids.add_button.disabled= False


	def _add(self):
		self.dismiss()
		
		btn =  Button(
			text = self.content_0,
			size_hint_y = None,
			height = 50,
			on_press = self.main_obj.pressed_layer0
		)
		self.main_obj.ids.layer0.add_widget(btn, index=1)
		self.main_obj.chapters.append(self.content_0)

		self.ids.content_layer0.text = ""
		self.ids.content_layer1.text = ""
		self.ids.content_layer2.text = ""
		self.ids.add_button.disabled= True
		self.data_storage()


	def data_storage(self):
		
		#list new directory name into dirs list
		dir_exst = False 
		with open("../data/dirs.txt","a+") as fp:
			for dirt in fp.readlines():
				if dirt[:-1].lower() == self.content_0.lower():
					dir_exst = True
			if not dir_exst:
				os.system(f"mkdir ../data/{self.content_0}")
				fp.write(self.content_0+'\n')
		fp.close()
		
		# list new filename into files list
		file_exst = False
		with open(f"../data/{self.content_0}/files.txt","a+") as fp:
			for file in fp.readlines():
				if file[:-1].lower() == self.content_1.lower():
					file_exst = True
			if not file_exst:
				fp.write(self.content_1+'\n')
		fp.close()

		#Create a new file and add data to it
		# with open(f"../data/{self.content_0}/{self.content_1}.txt","a") as fp:
		# 	fp.write(self.content_2+'\n')
		# fp.close()




class MyLayout(Widget):
	

	def __init__(self,**kwargs):
		super(MyLayout, self).__init__(**kwargs)
		self.chapters = []
		self.add_chapters()
		self.pop = CustomPopup()

	def add_chapters(self):
		try:
			with open("../data/dirs.txt",'r') as fp:
				for chapter in fp.readlines():
					btn =  Button(
						text = chapter[:-1],
						size_hint_y = None,
						height = 50,
						on_press = self.pressed_layer0
					)
					self.ids.layer0.add_widget(btn, index=1)
					self.chapters.append(chapter)
			fp.close()

		except FileNotFoundError:
			os.system("touch ../data/dirs.txt")

	def add_item_layer0(self):
		dataset = self.pop._open(self)

	def pressed_layer0(self, instance):
		dirname = instance.text

		self.ids.layer1.clear_widgets(children = None)

		self.ids.layer1.add_widget(Button(
			text = "+ADD TOPIC",
			size_hint_y=  None,
			height = 50,
		))
		with open(f"../data/{dirname}/files.txt",'r') as fp:
			for topic in fp.readlines():
				btn =  Button(
					text = topic[:-1],
					size_hint_y = None,
					height = 50,
					on_press = self.pressed_layer1
				)
				self.ids.layer1.add_widget(btn, index=1)


	def pressed_layer1(self, instance):
		pass

class LocalSearchApp(App):
	def build(self):
		return MyLayout()
		


if __name__ == "__main__":
	app = LocalSearchApp()
	app.run()

