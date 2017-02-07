import os, re

class TplSimple(object):
	def __init__(self, tpl):
		self.tpl = tpl

	def format(self, fields):
		if not isinstance(fields, dict):
			raise Exception('should fill template with a dictionary')
		content = self.tpl
		for k, v in fields.items():
			content = content.replace('{'+str(k)+'}', str(v))
			#content = re.sub(r'{\s*' + k + r'\s*}', v, content)
		return content

	def template(self):
		return self.tpl

class TplSimpleManager(object):
	def __init__(self, tpldir):
		if not os.path.exists(tpldir):
			raise Exception('template directory is invalid')
		self.tpldir = tpldir.rstrip(os.sep)
		self.tpls = {}

	def get_templatedir(self):
		return self.tpldir

	def get_template(self, name):
		tpl_path = os.sep.join([self.tpldir, name+'.tpl'])
		if not os.path.exists(tpl_path):
			raise Exception('template {} not existed'.format(name))
		if name not in self.tpls:
			with open(tpl_path, 'r', encoding='utf-8') as f:
				self.tpls[name] = TplSimple(f.read())
		return self.tpls[name]