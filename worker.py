import codecs
import sys




class Worker(object):

	def __init__(self):
		self.text = None
		self.special_chars = {'{','}','&','%','$','#','_','^','\\',' '}
		self.subs=[]
		self.tams=[]

	def decode(self,textF):
		self.text=textF
		i=0
		documento=False
		while(i<len(self.text)):
			if(self.text[i]=='%' and documento):
				fin=self.hunt(i,'\n')
				self.subs.append(i)
				self.tams.append(fin)
				#print("COMENTARIO:"+self.text[i:i+fin])
				i += fin
			if (self.text[i] == '\\' and (self.text[i - 1] != '\\')): #establece donde empieza el documento y quita los trozos de comando
				tam=self.detectCommand(i)
				bloque=self.text[i:i+tam]
				if(bloque=="\\begin{document}"):
					documento=True
					self.subs.clear()
					self.tams.clear()
					self.subs.append(0)
					self.tams.append(i+tam)
					i+=tam
					continue
				if (bloque == "\\begin{figure}"):
					fin=self.huntStr(i, "\\end{figure}")
					self.subs.append(i)
					self.tams.append(fin + len("\\end{figure}"))
					#print("FIGURA:"+self.text[i:i + fin + len("\\end{figure}")])
					i += fin + len("\\end{figure}")
					continue
				if (bloque == "\\begin{wrapfigure}"):
					fin=self.huntStr(i, "\\end{wrapfigure}")
					self.subs.append(i)
					self.tams.append(fin + len("\\end{wrapfigure}"))
					#print("FIGURA:"+self.text[i:i + fin + len("\\end{wrapfigure}")])
					i += fin + len("\\end{wrapfigure}")
					continue
				if (bloque == "\\begin{align*}"):
					fin=self.huntStr(i, "\\end{align*}")
					self.subs.append(i)
					self.tams.append(fin + len("\\end{align*}"))
					#print("FIGURA:"+self.text[i:i + fin + len("\\end{align*}")])
					i += fin + len("\\end{align*}")
					continue
				if (bloque == "\\begin{equation}"):
					fin=self.huntStr(i, "\\end{equation}")
					self.subs.append(i)
					self.tams.append(fin + len("\\end{equation}"))
					#print("FIGURA:"+self.text[i:i + fin + len("\\end{equation}")])
					i += fin + len("\\end{equation}")
					continue
				if(documento):
					pass
					#print(bloque)
				self.subs.append(i)
				if(self.text[i+tam]=='\\' and documento==True and (self.text[i+tam+1]=='\\' or self.text[i+tam+1]==' ')):
					tam+=2
				if (self.text[i + tam] == '\\' and documento == True and (
						self.text[i + tam + 1] == '\\' or self.text[i + tam + 1] == ' ')):
					tam += 2
				self.tams.append(tam)
				i+=tam
			if(documento):
				if(self.text[i]=='$'):
					fin=self.hunt(i+1,'$')
					#print("MATES:"+self.text[i:i+fin+2])
					self.subs.append(i)
					self.tams.append(fin+2)
					i+=fin+2
			#sys.stdout.write(self.text[i])
			i+=1
		nuevo=""
		i=0
		j=0
		hechas={}
		while(i<len(self.text)):
			if(i >= self.subs[j]):
				if(i<self.subs[j]+self.tams[j]):
					hechas[j]=self.text[i:self.subs[j]+self.tams[j]]
					i=self.subs[j]+self.tams[j]
					nuevo+="SUBB"+str(j)+"BBUS"
					j+=1;
			nuevo+=self.text[i]
			i+=1
		#print(nuevo)
		#TRADUCCION (captura de camposa traducir )
		saltables = {' ','\n',',','.','[',']',':','\t','(',')','?','¿'}
		i=0
		capturando= -1 #marca si esatmos capturando un campo y donde empezo la captura
		captura=""
		campos={}
		concampos=""
		j=0
		while (i < len(nuevo)):
			if (nuevo[i:i + 4] == "SUBB"):#si escontramos mates
				if(capturando!=-1): #si estamos capturando
					buffer=""
					while(captura[len(captura)-1] in saltables):
						buffer+=captura[-1:]#me guardo lo que quito
						captura=captura[:-1] #quitamos ultimos caracteres prescindibles
					if(len(captura)!=1 or captura == "y"): #rehacer bien esto
						campos[j]=captura
						concampos += "CAMP"+str(j)+"PMAC"+buffer[::-1]
						j+=1
					else:
						concampos += captura+buffer[::-1]
					captura = ""#capturado campo. reseteamos maquinaria
					capturando = -1
				concampos += nuevo[i:nuevo.index("BBUS", i + 4, i + 20) + 4]
				i = nuevo.index("BBUS", i + 4, i + 20) + 4 #saltamos mates
				continue
			if(nuevo[i] in saltables and capturando==-1): #si no estaba capturando, salto elementos prescindibles
				concampos+=nuevo[i]
				i+=1
				continue
			if(capturando==-1):
				capturando=i #empiezo a capturar
			captura+=nuevo[i]
			#concampos += nuevo[i]
			i+=1
		#print(concampos)
		self.swapCampos(campos)
		#RECONSTRUCCION
		i = 0
		reconstruido=""
		nuevo=concampos
		while (i < len(nuevo)):
			if(nuevo[i:i+4]=="CAMP"):
				j=int(nuevo[i+4:nuevo.index("PMAC",i+4,i+20)])
				reconstruido+=campos[j]
				i=nuevo.index("PMAC",i+4,i+20)+4
				continue
			if (nuevo[i:i + 4] == "SUBB"):
				j = int(nuevo[i + 4:nuevo.index("BBUS", i + 4, i + 20)])
				reconstruido += hechas[j]
				i = nuevo.index("BBUS", i + 4, i + 20) + 4
				continue
			reconstruido+=nuevo[i]
			i+=1
		print(reconstruido)


	def swapCampos(self,campos):
		#creamos xml
		xml=""
		i=0
		for campo in campos:
			xml+="<"+str(i)+">\""+campos[i]+"\"</"+str(i)+">\n"
			i+=1
		with codecs.open("out.xml", "w", "utf-8-sig") as temp:
			temp.write(xml)
			temp.close()
		input("Press Enter to continue...")
		newXml=""
		with codecs.open("trad.xml", "r", "utf-8-sig") as temp:
			newXml=temp.read()
			temp.close()
		i=0
		while(i<len(newXml)):
			j=int(newXml[i+1:newXml.find('>',i)])
			value=newXml[newXml.index(">\"",i)+2:newXml.index("\"</"+str(j)+">")]
			campos[j]=value
			i=newXml.index("\"</"+str(j)+">")+len("\"</"+str(j)+">")
			i+=1



	def detectCommand(self, posicion):
		i=0
		if(self.text[posicion+1] in self.special_chars): #comandos de un caracter
			#print("UN CARACTER"+self.text[posicion:posicion+2])
			return 2
		while posicion+i<len(self.text):
			if(self.text[posicion+i]=='{'): #detectamos con parentesis
				comando=self.text[posicion:posicion+i]
				fin=self.hunt(posicion+i,'}')
				#print("detectado \"" + self.text[posicion:posicion + i] + "\""+"con comando \""+self.text[posicion+i:posicion + i+fin+1]+"\"")
				return i+fin+1
			elif(self.text[posicion+i]=='['): #detectamos con corchete
				comando = self.text[posicion:posicion + i]
				fin = self.hunt(posicion + i, ']')
				if(i==1):
					fin=self.huntStr(posicion+i,"\\]")+1
				if(i!=1):
					pass #aqui tendria los argumentos a un comando
				#print("detectado \"" + self.text[posicion:posicion + i] + "\""+"con comando \"" + self.text[posicion + i:posicion + i + fin + 1 ]+ "\"")
				return i+fin+1
			elif (self.text[posicion + i] == '\n'):  # detectamos con salto linea
				#print("detectado \"" + self.text[posicion:posicion + i] + "\"")
				return i
			elif(self.text[posicion+i] in self.special_chars | {'=','(',')',','} and i!=0): #detectamos otros
				#print("detectado \""+self.text[posicion:posicion+i]+"\"")
				return i
			i+=1

	def hunt(self, posicion, char):  # metodo que persigue el fin de un bloque
		i = 0
		count = 1
		while posicion + i < len(self.text):
			if (char == '}' and i > 0 and self.text[posicion + i] == '{'):
				count += 1
			if (self.text[posicion + i] == char):
				count -= 1
				if (count < 1):
					return i
			i += 1
		print("ERROR posición "+str(posicion))
		return -1
	def huntStr(self, posicion, str): #metodo que persigue el fin de un bloque
		i = 0
		while posicion + i < len(self.text):
			if (self.text[posicion + i] == str[0]):
				if(self.text[posicion+i:posicion+i+len(str)]==str):
					return i
			i+=1
		print("ERROR")
		return -1
