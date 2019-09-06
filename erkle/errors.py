# MIT License

# Copyright (c) 2019 Dan Hetrick

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from erkle.hooks import hook

def raise_error_double_target_event(eobj,code,tokens):
	tokens.pop(0)	# remove server
	tokens.pop(0)	# reove message type
	tokens.pop(0)	# remove nick

	target = tokens.pop(0)
	target2 = tokens.pop(0)
	reason = ' '.join(tokens)
	reason = reason[1:]

	hook.call("error",eobj,code,f"{target} {target2}",reason)

def raise_error_target_event(eobj,code,tokens):
	tokens.pop(0)	# remove server
	tokens.pop(0)	# reove message type
	tokens.pop(0)	# remove nick

	target = tokens.pop(0)
	reason = ' '.join(tokens)
	reason = reason[1:]

	hook.call("error",eobj,code,target,reason)

def raise_error_event(eobj,code,line):
	parsed = line.split(':')
	if len(parsed)>=2:
		reason = parsed[1]
	else:
		reason = "Unknown error"

	hook.call("error",eobj,code,None,reason)

def handle_errors(eobj,line):

	tokens = line.split()

	if tokens[1]=="400":
		hook.call("error",eobj,"400",None,"Uknown error")
		return True

	if tokens[1]=="401":
		raise_error_target_event(eobj,"401",tokens)
		return True

	if tokens[1]=="402":
		raise_error_target_event(eobj,"402",tokens)
		return True

	if tokens[1]=="403":
		raise_error_target_event(eobj,"403",tokens)
		return True

	if tokens[1]=="404":
		raise_error_target_event(eobj,"404",tokens)
		return True

	if tokens[1]=="405":
		raise_error_target_event(eobj,"405",tokens)
		return True

	if tokens[1]=="406":
		raise_error_target_event(eobj,"406",tokens)
		return True

	if tokens[1]=="407":
		raise_error_target_event(eobj,"407",tokens)
		return True

	if tokens[1]=="409":
		raise_error_event(eobj,"409",line)
		return True

	if tokens[1]=="411":
		raise_error_event(eobj,"411",line)
		return True

	if tokens[1]=="412":
		raise_error_event(eobj,"412",line)
		return True

	if tokens[1]=="413":
		raise_error_target_event(eobj,"413",tokens)
		return True

	if tokens[1]=="414":
		raise_error_target_event(eobj,"414",tokens)
		return True

	if tokens[1]=="415":
		raise_error_target_event(eobj,"415",tokens)
		return True

	if tokens[1]=="421":
		raise_error_target_event(eobj,"421",tokens)
		return True

	if tokens[1]=="422":
		raise_error_event(eobj,"422",line)
		return True

	if tokens[1]=="423":
		raise_error_target_event(eobj,"423",tokens)
		return True

	if tokens[1]=="424":
		raise_error_event(eobj,"424",line)
		return True

	if tokens[1]=="431":
		raise_error_event(eobj,"431",line)
		return True

	if tokens[1]=="432":
		raise_error_target_event(eobj,"432",tokens)
		return True

	if tokens[1]=="436":
		raise_error_target_event(eobj,"436",tokens)
		return True

	if tokens[1]=="441":
		raise_error_double_target_event(eobj,"441",tokens)
		return True

	if tokens[1]=="442":
		raise_error_target_event(eobj,"442",tokens)
		return True

	if tokens[1]=="444":
		raise_error_target_event(eobj,"444",tokens)
		return True

	if tokens[1]=="445":
		raise_error_event(eobj,"445",line)
		return True

	if tokens[1]=="446":
		raise_error_event(eobj,"446",line)
		return True

	if tokens[1]=="451":
		raise_error_event(eobj,"451",line)
		return True

	if tokens[1]=="461":
		raise_error_target_event(eobj,"461",tokens)
		return True

	if tokens[1]=="462":
		raise_error_event(eobj,"462",line)
		return True

	if tokens[1]=="463":
		raise_error_event(eobj,"463",line)
		return True

	if tokens[1]=="464":
		raise_error_event(eobj,"464",line)
		return True

	if tokens[1]=="465":
		raise_error_event(eobj,"465",line)
		return True

	if tokens[1]=="467":
		raise_error_target_event(eobj,"467",tokens)
		return True

	if tokens[1]=="471":
		raise_error_target_event(eobj,"471",tokens)
		return True

	if tokens[1]=="472":
		raise_error_target_event(eobj,"472",tokens)
		return True

	if tokens[1]=="473":
		raise_error_target_event(eobj,"473",tokens)
		return True

	if tokens[1]=="474":
		raise_error_target_event(eobj,"474",tokens)
		return True

	if tokens[1]=="475":
		raise_error_target_event(eobj,"475",tokens)
		return True

	if tokens[1]=="476":
		raise_error_target_event(eobj,"476",tokens)
		return True

	if tokens[1]=="478":
		raise_error_double_target_event(eobj,"478",tokens)
		return True

	if tokens[1]=="481":
		raise_error_event(eobj,"481",line)
		return True

	if tokens[1]=="482":
		raise_error_target_event(eobj,"482",tokens)
		return True

	if tokens[1]=="483":
		raise_error_event(eobj,"483",line)
		return True

	if tokens[1]=="485":
		raise_error_event(eobj,"481",line)
		return True

	if tokens[1]=="491":
		raise_error_event(eobj,"491",line)
		return True

	if tokens[1]=="501":
		raise_error_event(eobj,"501",line)
		return True

	if tokens[1]=="502":
		raise_error_event(eobj,"502",line)
		return True

	return False
