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
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

Builder.load_file('design.kv')


BACKGROUND_COLOR = '#ffffff'

class CustomErrorPopup(Popup):
	pass

class RoundedButton(Button):
	pass

class RoundedButtonGreen(Button):
	pass

class RoundedButtonRed(Button):
	pass


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
		pat = re.compile("^[a-z0-9]{1,15}$")

		#validating input data
		if (not pat.match(self.dirname) or not pat.match(self.filename)):
			self.ids.no_validate.text = "Invalid input for \nChapter or Topic"
			return
		elif (not self.info):
			self.ids.no_validate.text = "Content field cannot be empty!!"
			return

		#if validated, enable add button
		self.ids.no_validate.text = ""
		self.ids.add_button.disabled= False


	def _add(self):
		self.dismiss()

		# set the text fields of the popup to empty  
		self.ids._chapter.text = ""
		self.ids._topic.text = ""
		self.ids._info.text = ""

		#disable add button once data is added
		self.ids.add_button.disabled= True
		self.data_storage()


	def data_storage(self):

		#lists new directory(chapter) name into dirs list
		dir_exst = False 
		with open("../data/dirs_list.txt","r+") as fp:

			#check if the directory is already present
			for dirt in fp.readlines():
				if dirt[:-1] == self.dirname:
					dir_exst = True
			
			# if not, create a dir and update dirs list
			if not dir_exst:

				# create directory
				os.system(f"mkdir ../data/{self.dirname}")

				#updating dir list and add a button to the main object
				fp.write(self.dirname+'\n')
				btn = RoundedButton(
					text = self.dirname.upper(),
					size_hint_y = None,
					height = 50,
					on_press = self.main_obj.pressed_chapter
				)
				self.main_obj.ids.chapter_.add_widget(btn, index =1)
		fp.close()
		
		# lists new filename(topic) into files list and creates it if dosen't exist
		file_exst = False
		try:
			with open(f"../data/{self.dirname}/files_list.txt","r+") as fp:

				# checks if file already listed in files
				for file in fp.readlines():
					if file[:-1] == self.filename:
						file_exst = True

				#write if not
				if not file_exst:
					fp.write(self.filename+'\n')
			fp.close()

		except FileNotFoundError:

			#creates a new file and update it
			with open(f"../data/{self.dirname}/files_list.txt","w") as fp:
				fp.write(self.filename+'\n')
			fp.close()


		# Update the topic file, creates if dosen't exist
		with open(f"../data/{self.dirname}/{self.filename}.txt","a") as fp:
			fp.write(self.info+'\n')
		fp.close()



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

		# if dir or filename is not given 
		if (not dirname or not filename):
			error_pop.ids.err.text = "Input fields cannot be empty"
			error_pop.open()


		# deletes the whole dir(chapter)
		if (filename == "*" or filename == "all"):
			dir_exst = False

			with open("../data/dirs_list.txt","r+") as fp:
				
				#look for dir in dirs lists
				for dirt in fp.readlines():
					if dirt[:-1] == dirname:
						dir_exst = True

				#alert if non-existant
				if not dir_exst:
					error_pop.ids.err.text = "Chapter Not Found"
					error_pop.open()
				else:
					# removes if found
					fp.seek(0,0)
					ft = open("../data/dirs2.txt", "w")
					for dirt in fp.readlines():
						if dirt[:-1] == dirname:
							continue
						ft.write(dirt)
					ft.close()
			fp.close()

			if dir_exst:
				# removes the whole chapter if found
				os.remove("../data/dirs_list.txt")
				os.rename("../data/dirs2.txt", "../data/dirs_list.txt")
				os.system(f"rm -rf ../data/{dirname}")

		
		# removes a topic
		else:
			file_exst = False
			try:
				with open(f"../data/{dirname}/files_list.txt","r+") as fp:
					
					#look for topic
					for file in fp.readlines():
						if file[:-1] == filename:
							file_exst = True

					#raises an error if non existant
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
				fp.close()
				if file_exst:
					os.remove(f"../data/{dirname}/files_list.txt")
					os.rename(f"../data/{dirname}/files2.txt", f"../data/{dirname}/files_list.txt")
					os.remove(f"../data/{dirname}/{filename}.txt")

			except:
				error_pop.ids.err.text = "Chapter Not Found"
				error_pop.open()

		self.dismiss()

		#updates the main object
		self.main_obj.add_chapters()


class MyLayout(Widget):
	

	def __init__(self,**kwargs):
		super(MyLayout, self).__init__(**kwargs)

		#add chapters to the screen
		self.add_chapters()
		self.add_popup = CustomAddPopup()
		self.remove_popup = CustomRemovePopup()

	def add_chapters(self):
		self.ids.chapter_.clear_widgets(children = None)
		self.ids.topic_.clear_widgets(children = None)
		self.ids.info_.text = ""
		add_btn = RoundedButtonGreen(
			text = "+ADD",
			size_hint_y = None,
			height = 50,
			on_press = self.add_item,
		)
		self.ids.chapter_.add_widget(add_btn)
		rmv_btn = RoundedButtonRed(
			text = "-REMOVE",
			size_hint_y = None,
			height = 50,
			on_press = self.remove_item
		)
		self.ids.chapter_.add_widget(rmv_btn)
		try:
			with open("../data/dirs_list.txt",'r') as fp:
				for line in fp.readlines():
					btn =  RoundedButton(
						text = line[:-1].upper(),
						size_hint_y = None,
						height = 50,
						on_press = self.pressed_chapter
					)
					self.ids.chapter_.add_widget(btn, index = 1)
			fp.close()

		except FileNotFoundError:
			os.system("touch ../data/dirs_list.txt")

		self.ids.info_.disabled = True


	def add_item(self, instance):
		self.add_popup._open(self)

	def remove_item(self, instance):
		self.remove_popup._open(self)

	def pressed_chapter(self, instance):
		self.dirname = instance.text.lower()
		self.ids.label1.text = instance.text
		self.ids.label2.text = "TOPICS"
		self.ids.topic_.clear_widgets(children = None)
		self.ids.info_.text = ""
		self.ids.info_.disabled = True

		with open(f"../data/{self.dirname}/files_list.txt",'r') as fp:
			for topic in fp.readlines():
				btn =  RoundedButton(
					text = topic[:-1].upper(),
					size_hint_y = None,
					height = 50,
					on_press = self.pressed_topic
				)
				self.ids.topic_.add_widget(btn)


	def pressed_topic(self, instance):
		self.filename = instance.text.lower()
		self.ids.label2.text = instance.text
		self.ids.info_.text = ""
		with open(f"../data/{self.dirname}/{self.filename}.txt", 'r') as fp:
			self.ids.info_.text = ''.join(fp.readlines())
		self.ids.info_.disabled = False
		fp.close()

	def update_content(self):
		new_content = self.ids.info_.text
		if (not new_content):
			return
		with open(f"../data/{self.dirname}/{self.filename}.txt", 'w') as fp: 
			fp.write(new_content)
		fp.close()		

class LocalSearchApp(App):
	def build(self):
		Window.clearcolor = get_color_from_hex(BACKGROUND_COLOR)
		return MyLayout()

if __name__ == "__main__":
	app = LocalSearchApp()
	app.run()

