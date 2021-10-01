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

class CustomAddPopup(Popup):
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
		pat = re.compile(".{1,10}$")
		if (not pat.match(self.dirname) or not pat.match(self.filename)):
			self.ids.no_validate.text = "Invalid input for \n Chapter or Topic"
			return
		elif (not self.info):
			self.ids.no_validate.text = "Info field cannot be empty!!"
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
				self.main_obj.ids.chapter_.add_widget(btn, index =1)
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

class CustomErrorPopup(Popup):
	pass


class CustomRemovePopup(Popup):
	def __init__(self, **kwargs):
		super(CustomRemovePopup, self).__init__(**kwargs)

	def _open(self, main):
		self.main_obj = main
		self.open()

	def _remove_(self):
		dirname = self.ids._chapter_.text.strip().lower()
		filename = self.ids._topic_.text.strip().lower()
		error_pop = CustomErrorPopup()
		self.ids._chapter_.text = ""
		self.ids._topic_.text = ""

		if (not dirname or not filename):
			error_pop.ids.err.text = "Input fields cannot be empty"
			error_pop.open()

		if (filename == "*" or filename == "all"):
			dir_exst = False 
			with open("../data/dirs.txt","r+") as fp:
				for dirt in fp.readlines():
					if dirt[:-1] == dirname:
						dir_exst = True
				if not dir_exst:
					error_pop.ids.err.text = "Chapter Not Found"
					error_pop.open()
				else:
					fp.seek(0,0)
					ft = open("../data/dirs2.txt", "w")
					for dirt in fp.readlines():
						if dirt[:-1] == dirname:
							continue
						ft.write(dirt)
					ft.close()
					os.remove("../data/dirs.txt")
					os.rename("../data/dirs2.txt", "../data/dirs.txt")
					os.system(f"rm -rf ../data/{dirname}")
			fp.close()
		
		else:
			file_exst = False
			try:
				with open(f"../data/{dirname}/files.txt","r+") as fp:
					for file in fp.readlines():
						if file[:-1] == filename:
							file_exst = True
					if not file_exst:
						error_pop.ids.err.text = "Topic Not Found"
						error_pop.open()
					else:
						fp.seek(0,0)
						ft = open(f"../data/{dirname}/files2.txt","w")
						for file in fp.readlines():
							if file[:-1] == filename:
								continue
							ft.write(file)
						ft.close()
						os.remove(f"../data/{dirname}/files.txt")
						os.rename(f"../data/{dirname}/files2.txt", f"../data/{dirname}/files.txt")
						os.remove(f"../data/{dirname}/{filename}.txt")
				fp.close()
			except:
				error_pop.ids.err.text = "Chapter Not Found"
				error_pop.open()

		self.dismiss()
		self.main_obj.add_chapters()


class MyLayout(Widget):
	

	def __init__(self,**kwargs):
		super(MyLayout, self).__init__(**kwargs)
		self.add_chapters()
		self.add_popup = CustomAddPopup()
		self.remove_popup = CustomRemovePopup()

	def add_chapters(self):
		self.ids.chapter_.clear_widgets(children = None)
		self.ids.topic_.clear_widgets(children = None)
		self.ids.info_.text = ""
		add_btn = Button(
			text = "+ADD",
			size_hint_y = None,
			height = 50,
			on_press = self.add_item
		)
		self.ids.chapter_.add_widget(add_btn)
		rmv_btn = Button(
			text = "-REMOVE",
			size_hint_y = None,
			height = 50,
			on_press = self.remove_item
		)
		self.ids.chapter_.add_widget(rmv_btn)
		try:
			with open("../data/dirs.txt",'r') as fp:
				for line in fp.readlines():
					btn =  Button(
						text = line[:-1].upper(),
						size_hint_y = None,
						height = 50,
						on_press = self.pressed_chapter
					)
					self.ids.chapter_.add_widget(btn, index = 1)
			fp.close()

		except FileNotFoundError:
			os.system("touch ../data/dirs.txt")

	def add_item(self, instance):
		self.add_popup._open(self)

	def remove_item(self, instance):
		self.remove_popup._open(self)

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
				self.ids.topic_.add_widget(btn)


	def pressed_topic(self, instance):
		filename = instance.text.lower()
		self.ids.info_.text = ""
		with open(f"../data/{self.dirname}/{filename}.txt") as fp:
			self.ids.info_.text = ''.join(fp.readlines())
		fp.close()
		

class LocalSearchApp(App):
	def build(self):
		return MyLayout()

if __name__ == "__main__":
	app = LocalSearchApp()
	app.run()

