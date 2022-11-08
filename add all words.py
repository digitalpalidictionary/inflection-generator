#!/usr/bin/env python3.10
# coding: utf-8

import pandas as pd
from modules import clean_machine
import pickle
from timeis import timeis, tic, toc, white, green, yellow, line, red
import re

tic()
print(f"{timeis()} {line}")
print(f"{timeis()} {yellow}finding all missing words")
print(f"{timeis()} {line}")

def make_text_list():
	print(f"{timeis()} {green}making text list", end=" ")
	text_list = []
	text_path = "../Cst4/txt/"
	texts = []
	# texts += ["vin01m.mul.xml.txt"]  # VIN1
	# texts += ["vin02m1.mul.xml.txt"]  # VIN2
	# texts += ["vin02m2.mul.xml.txt"]  # VIN3
	# texts += ["vin02m3.mul.xml.txt"]  # VIN4
	# texts += ["vin02m4.mul.xml.txt"]  # VIN5

	# texts = ["s0101m.mul.xml.txt"]  # DN1
	# texts += ["s0102m.mul.xml.txt"]  # DN2
	# texts += ["s0103m.mul.xml.txt"]  # DN3

	# texts += ["s0201m.mul.xml.txt"]  # MN1
	# texts = ["s0202m.mul.xml.txt"]  # MN2
	# texts = ["s0203m.mul.xml.txt"]  # MN3

	# texts = ["s0301m.mul.xml.txt"]  # SN1
	# texts = ["s0302m.mul.xml.txt"]  # SN2
	# texts = ["s0303m.mul.xml.txt"]  # SN3
	# texts = ["s0304m.mul.xml.txt"]  # SN4
	# texts = ["s0305m.mul.xml.txt"]  # SN5

	# texts += ["s0401m.mul.xml.txt"]  # AN1 mūla
	# texts += ["s0402m1.mul.xml.txt"]  # AN2 mūla
	# texts += ["s0402m2.mul.xml.txt"]  # AN3 mūla
	# texts += ["s0402m3.mul.xml.txt"]  # AN4 mūla
	# texts += ["s0403m1.mul.xml.txt"]  # AN5 mūla
	# texts += ["s0403m2.mul.xml.txt"]  # AN6 mūla
	# texts += ["s0403m3.mul.xml.txt"]  # AN7 mūla
	# texts += ["s0404m1.mul.xml.txt"]  # AN8 mūla
	# texts += ["s0404m2.mul.xml.txt"]  # AN9 mūla
	# texts += ["s0404m3.mul.xml.txt"]  # AN10 mūla
	# texts += ["s0404m4.mul.xml.txt"]  # AN11 mūla

	for text in texts:
		with open (f"{text_path}{text}", "r") as f:
			text_read = f.read()
		clean_text = clean_machine(text_read)
		text_list += clean_text.split()
	
	print(f"{white}{len(text_list)}")
	return text_list


text_list = make_text_list()

def make_sc_text_list():
	print(f"{timeis()} {green}making sutta central text list", end=" ")
	sc_text_list = []
	sc_path = "../Tipitaka-Pali-Projector/tipitaka_projector_data/pali/"
	
	sc_texts = []
	# sc_texts += ["11010a.js"]  # VIN1
	# sc_texts += ["11020a.js"]  # VIN2
	# sc_texts += ["11030a.js"]  # VIN3
	# sc_texts += ["11040a.js"]  # VIN4
	# sc_texts += ["11050a.js"]  # VIN5

	# sc_texts += ["21010a.js"]  # DN1
	# sc_texts += ["21020a.js"]  # DN2
	# sc_texts += ["21030a.js"]  # DN3

	# sc_texts += ["31010a.js"]  # MN1
	# sc_texts += ["31020a.js"]  # MN2
	# sc_texts += ["31030a.js"]  # MN3

	# sc_texts += ["41010a.js"]  # SN1
	# sc_texts += ["41020a.js"]  # SN2
	# sc_texts += ["41030a.js"]  # SN3
	# sc_texts += ["41040a.js"]  # SN4
	# sc_texts += ["41050a.js"]  # SN5

	# sc_texts += ["51010a.js"]  # AN1
	# sc_texts += ["51020a.js"]  # AN2
	# sc_texts += ["51030a.js"]  # AN3
	# sc_texts += ["51040a.js"]  # AN4
	# sc_texts += ["51050a.js"]  # AN5
	# sc_texts += ["51060a.js"]  # AN6
	# sc_texts += ["51070a.js"]  # AN7
	# sc_texts += ["51080a.js"]  # AN8
	# sc_texts += ["51090a.js"]  # AN9
	# sc_texts += ["51100a.js"]  # AN10
	# sc_texts += ["51110a.js"]  # AN11

	# sc_texts += ["61080a.js"]  # TH
	# sc_texts += ["61090a.js"]  # THI

	for sc_text in sc_texts:
		with open(f"{sc_path}{sc_text}", "r") as f:
			text_read = f.read()
		text_read = re.sub("var P_HTM.+", "", text_read)
		text_read = re.sub("""P_HTM\\[\\d+\\]="\\*""", "", text_read)
		text_read = re.sub("""\\*\\*.+;""", "", text_read)
		text_read = re.sub("\n", " ", text_read)
		text_read = text_read.lower()
		clean_text = clean_machine(text_read)
		sc_text_list += clean_text.split()

	# print(sc_text_list)
	print(f"{white}{len(sc_text_list)}")
	return sc_text_list


sc_text_list = make_sc_text_list()


def make_bjt_text_list():
	print(f"{timeis()} {green}making buddhajayanti text list", end=" ")
	text_list = []
	text_path = "../../../../git/tipitaka.lk/public/static/text roman/"
	
	texts = []
	# # pārājika
	# texts += ["vp-prj.txt"]
	# texts += ["vp-prj-2-3.txt"]
	# texts += ["vp-prj-3.txt"]
	# texts += ["vp-prj-3-4.txt"]
	# texts += ["vp-prj-4.txt"]

	# # pācittiya
	# texts += ["vp-pct.txt"]
	# texts += ["vp-pct-1-1-5.txt"]
	# texts += ["vp-pct-1-2.txt"]
	# texts += ["vp-pct-2.txt"]
	# texts += ["vp-pct-2-4-3.txt"]
	# texts += ["vp-pct-2-5.txt"]
	
	# # mahāvagga
	# texts += ["vp-mv.txt"]
	# texts += ["vp-mv-2.txt"]
	# texts += ["vp-mv-4.txt"]
	# texts += ["vp-mv-6.txt"]
	# texts += ["vp-mv-7.txt"]
	# texts += ["vp-mv-9.txt"]

	# # cūlavagga
	# texts += ["vp-cv.txt"]
	# texts += ["vp-cv-3.txt"]
	# texts += ["vp-cv-5.txt"]
	# texts += ["vp-cv-8.txt"]

	# # parivāra
	# texts += ["vp-pv.txt"]
	# texts += ["vp-pv-2.txt"]
	# texts += ["vp-pv-5.txt"]
	# texts += ["vp-pv-14.txt"]
	

	# # dīgha
	# texts += ["dn-1.txt"]
	# texts += ["dn-1-3.txt"]
	# texts += ["dn-1-6.txt"]
	# texts += ["dn-1-11.txt"]

	# texts += ["dn-2.txt"]
	# texts += ["dn-2-3.txt"]
	# texts += ["dn-2-4.txt"]
	# texts += ["dn-2-7.txt"]

	# texts += ["dn-3.txt"]
	# texts += ["dn-3-10.txt"]
	# texts += ["dn-3-5.txt"]

	# # majjhima
	# texts += ["mn-1-1.txt"]
	# texts += ["mn-1-2.txt"]
	# texts += ["mn-1-3.txt"]
	# texts += ["mn-1-4.txt"]
	# texts += ["mn-1-5.txt"]

	# texts += ["mn-2-1.txt"]
	# texts += ["mn-2-2.txt"]
	# texts += ["mn-2-3.txt"]
	# texts += ["mn-2-4.txt"]
	# texts += ["mn-2-5.txt"]

	# texts += ["mn-3-1.txt"]
	# texts += ["mn-3-2.txt"]
	# texts += ["mn-3-3.txt"]
	# texts += ["mn-3-4.txt"]
	# texts += ["mn-3-5.txt"]

	# # saṃyutta
	# texts += ["sn-1.txt"]
	# texts += ["sn-1-3.txt"]
	# texts += ["sn-1-7.txt"]
	
	# texts += ["sn-2.txt"]
	# texts += ["sn-2-1-5.txt"]
	# texts += ["sn-2-2.txt"]
	# texts += ["sn-2-5.txt"]
	
	# texts += ["sn-3.txt"]
	# texts += ["sn-3-1-2.txt"]
	# texts += ["sn-3-1-3.txt"]
	# texts += ["sn-3-2.txt"]
	# texts += ["sn-3-7.txt"]
	
	# texts += ["sn-4.txt"]
	# texts += ["sn-4-1-12.txt"]
	# texts += ["sn-4-2.txt"]
	# texts += ["sn-4-8.txt"]
	
	# texts += ["sn-5.txt"]
	# texts += ["sn-5-11.txt"]
	# texts += ["sn-5-12.txt"]
	# texts += ["sn-5-2.txt"]
	# texts += ["sn-5-3.txt"]
	# texts += ["sn-5-4.txt"]
	# texts += ["sn-5-7.txt"]

	# # aṅguttara
	# texts += ["an-1.txt"]
	# texts += ["an-2.txt"]
	# texts += ["an-3-2.txt"]
	# texts += ["an-3-3.txt"]
	# texts += ["an-3.txt"]
	# texts += ["an-4-2.txt"]
	# texts += ["an-4-3.txt"]
	# texts += ["an-4-4.txt"]
	# texts += ["an-4-5.txt"]
	# texts += ["an-4.txt"]
	# texts += ["an-5-2.txt"]
	# texts += ["an-5-3.txt"]
	# texts += ["an-5-4.txt"]
	# texts += ["an-5-5.txt"]
	# texts += ["an-5.txt"]
	# texts += ["an-6-2.txt"]
	# texts += ["an-6.txt"]
	# texts += ["an-7-2.txt"]
	# texts += ["an-7.txt"]
	# texts += ["an-8-2.txt"]
	# texts += ["an-8.txt"]
	# texts += ["an-9.txt"]
	# texts += ["an-10-2.txt"]
	# texts += ["an-10-3.txt"]
	# texts += ["an-10-4.txt"]
	# texts += ["an-10-5.txt"]
	# texts += ["an-10.txt"]
	# texts += ["an-11.txt"]

	# # khuddaka
	# texts += ["kn-ap-1-19.txt"]
	# texts += ["kn-ap-1-33.txt"]
	# texts += ["kn-ap-1-41.txt"]
	# texts += ["kn-ap-1-45.txt"]
	# texts += ["kn-ap-1-5.txt"]
	# texts += ["kn-ap-1-53.txt"]
	# texts += ["kn-ap-2.txt"]
	# texts += ["kn-ap.txt"]
	# texts += ["kn-bv.txt"]
	# texts += ["kn-cp.txt"]
	# texts += ["kn-dhp.txt"]
	# texts += ["kn-iti.txt"]
	# texts += ["kn-jat-11.txt"]
	# texts += ["kn-jat-15.txt"]
	# texts += ["kn-jat-18.txt"]
	# texts += ["kn-jat-22-10.txt"]
	# texts += ["kn-jat-22-6.txt"]
	# texts += ["kn-jat-22.txt"]
	# texts += ["kn-jat-5.txt"]
	# texts += ["kn-jat.txt"]
	# texts += ["kn-khp.txt"]
	# texts += ["kn-mn-14.txt"]
	# texts += ["kn-mn-6.txt"]
	# texts += ["kn-mn.txt"]
	# texts += ["kn-nc-18.txt"]
	# texts += ["kn-nc-5.txt"]
	# texts += ["kn-nc.txt"]
	# texts += ["kn-nett-3-3.txt"]
	# texts += ["kn-nett.txt"]
	# texts += ["kn-petk-6.txt"]
	# texts += ["kn-petk.txt"]
	# texts += ["kn-ps-1-1-17.txt"]
	# texts += ["kn-ps-1-2.txt"]
	# texts += ["kn-ps-1-3.txt"]
	# texts += ["kn-ps-1-4.txt"]
	# texts += ["kn-ps-1-5.txt"]
	# texts += ["kn-ps-1-6.txt"]
	# texts += ["kn-ps-2.txt"]
	# texts += ["kn-ps-3.txt"]
	# texts += ["kn-ps.txt"]
	# texts += ["kn-pv.txt"]
	# texts += ["kn-snp-2.txt"]
	# texts += ["kn-snp-3.txt"]
	# texts += ["kn-snp-4.txt"]
	# texts += ["kn-snp-5.txt"]
	# texts += ["kn-snp.txt"]
	# texts += ["kn-thag-11.txt"]
	# texts += ["kn-thag.txt"]
	# texts += ["kn-thig.txt"]
	# texts += ["kn-ud.txt"]
	# texts += ["kn-vv.txt"]

	# # abhidhamma
	# texts += ["ap-dhk.txt"]
	# texts += ["ap-dhs-3.txt"]
	# texts += ["ap-dhs-5.txt"]
	# texts += ["ap-dhs.txt"]
	# texts += ["ap-kvu-1-2.txt"]
	# texts += ["ap-kvu-11.txt"]
	# texts += ["ap-kvu-15.txt"]
	# texts += ["ap-kvu-19.txt"]
	# texts += ["ap-kvu-2.txt"]
	# texts += ["ap-kvu-3.txt"]
	# texts += ["ap-kvu-5.txt"]
	# texts += ["ap-kvu-8.txt"]
	# texts += ["ap-kvu.txt"]
	# texts += ["ap-pat-1-12.txt"]
	# texts += ["ap-pat-2-47.txt"]
	# texts += ["ap-pat-2-83.txt"]
	# texts += ["ap-pat-2.txt"]
	# texts += ["ap-pat-3.txt"]
	# texts += ["ap-pat-4.txt"]
	# texts += ["ap-pat.txt"]
	# texts += ["ap-pug.txt"]
	# texts += ["ap-vbh-10.txt"]
	# texts += ["ap-vbh-14.txt"]
	# texts += ["ap-vbh-17.txt"]
	# texts += ["ap-vbh-2.txt"]
	# texts += ["ap-vbh-6.txt"]
	# texts += ["ap-vbh.txt"]
	# texts += ["ap-yam-10-3-4.txt"]
	# texts += ["ap-yam-10-3.txt"]
	# texts += ["ap-yam-10-4.txt"]
	# texts += ["ap-yam-10.txt"]
	# texts += ["ap-yam-3.txt"]
	# texts += ["ap-yam-4.txt"]
	# texts += ["ap-yam-6.txt"]
	# texts += ["ap-yam-7-5.txt"]
	# texts += ["ap-yam-7.txt"]
	# texts += ["ap-yam-8.txt"]
	# texts += ["ap-yam.txt"]

	# # commentary 
	# texts += ["atta-an-1-14-3.txt"]
	# texts += ["atta-an-1-15.txt"]
	# texts += ["atta-an-1.txt"]
	# texts += ["atta-an-10.txt"]
	# texts += ["atta-an-11.txt"]
	# texts += ["atta-an-2.txt"]
	# texts += ["atta-an-3.txt"]
	# texts += ["atta-an-4.txt"]
	# texts += ["atta-an-5.txt"]
	# texts += ["atta-an-6.txt"]
	# texts += ["atta-an-7.txt"]
	# texts += ["atta-an-8.txt"]
	# texts += ["atta-an-9.txt"]
	# texts += ["atta-ap-dhk.txt"]
	# texts += ["atta-ap-dhs-3.txt"]
	# texts += ["atta-ap-dhs.txt"]
	# texts += ["atta-ap-kvu.txt"]
	# texts += ["atta-ap-pat.txt"]
	# texts += ["atta-ap-pug.txt"]
	# texts += ["atta-ap-vbh-8.txt"]
	# texts += ["atta-ap-vbh.txt"]
	# texts += ["atta-ap-yam.txt"]
	# texts += ["atta-dn-1-2.txt"]
	# texts += ["atta-dn-1.txt"]
	# texts += ["atta-dn-2-4.txt"]
	# texts += ["atta-dn-2.txt"]
	# texts += ["atta-dn-3.txt"]
	# texts += ["atta-kn-ap-1-2.txt"]
	# texts += ["atta-kn-ap.txt"]
	# texts += ["atta-kn-bv.txt"]
	# texts += ["atta-kn-cp-3.txt"]
	# texts += ["atta-kn-cp.txt"]
	# texts += ["atta-kn-dhp-19.txt"]
	# texts += ["atta-kn-dhp-4.txt"]
	# texts += ["atta-kn-dhp-9.txt"]
	# texts += ["atta-kn-dhp.txt"]
	# texts += ["atta-kn-iti-3.txt"]
	# texts += ["atta-kn-iti.txt"]
	# texts += ["atta-kn-jat-1-6.txt"]
	# texts += ["atta-kn-jat-14.txt"]
	# texts += ["atta-kn-jat-17.txt"]
	# texts += ["atta-kn-jat-2.txt"]
	# texts += ["atta-kn-jat-21.txt"]
	# texts += ["atta-kn-jat-22-5.txt"]
	# texts += ["atta-kn-jat-22-9.txt"]
	# texts += ["atta-kn-jat-22.txt"]
	# texts += ["atta-kn-jat-3.txt"]
	# texts += ["atta-kn-jat-4.txt"]
	# texts += ["atta-kn-jat-6.txt"]
	# texts += ["atta-kn-jat-9.txt"]
	# texts += ["atta-kn-jat.txt"]
	# texts += ["atta-kn-khp.txt"]
	# texts += ["atta-kn-mn-6.txt"]
	# texts += ["atta-kn-mn.txt"]
	# texts += ["atta-kn-nc.txt"]
	# texts += ["atta-kn-nett.txt"]
	# texts += ["atta-kn-ps-1-1-2.txt"]
	# texts += ["atta-kn-ps-1-2.txt"]
	# texts += ["atta-kn-ps-2.txt"]
	# texts += ["atta-kn-ps.txt"]
	# texts += ["atta-kn-pv.txt"]
	# texts += ["atta-kn-snp-2.txt"]
	# texts += ["atta-kn-snp-3.txt"]
	# texts += ["atta-kn-snp.txt"]
	# texts += ["atta-kn-thag-15.txt"]
	# texts += ["atta-kn-thag-2.txt"]
	# texts += ["atta-kn-thag-5.txt"]
	# texts += ["atta-kn-thag.txt"]
	# texts += ["atta-kn-thig.txt"]
	# texts += ["atta-kn-ud-4.txt"]
	# texts += ["atta-kn-ud.txt"]
	# texts += ["atta-kn-vv-4.txt"]
	# texts += ["atta-kn-vv.txt"]
	# texts += ["atta-mn-1-1-6.txt"]
	# texts += ["atta-mn-1-2.txt"]
	# texts += ["atta-mn-1-4.txt"]
	# texts += ["atta-mn-1.txt"]
	# texts += ["atta-mn-2-3.txt"]
	# texts += ["atta-mn-2.txt"]
	# texts += ["atta-mn-3.txt"]
	# texts += ["atta-sn-1-5.txt"]
	# texts += ["atta-sn-1.txt"]
	# texts += ["atta-sn-2.txt"]
	# texts += ["atta-sn-3.txt"]
	# texts += ["atta-sn-4.txt"]
	# texts += ["atta-sn-5.txt"]
	# texts += ["atta-vp-cv.txt"]
	# texts += ["atta-vp-mv.txt"]
	# texts += ["atta-vp-pct.txt"]
	# texts += ["atta-vp-prj-2.txt"]
	# texts += ["atta-vp-prj-3.txt"]
	# texts += ["atta-vp-prj.txt"]
	# texts += ["atta-vp-pv.txt"]
	
	# # visuddhimagga
	# texts += ["anya-vm-1.txt"]
	# texts += ["anya-vm-12.txt"]


	for text in texts:
		with open(f"{text_path}{text}", "r") as f:
			text_read = f.read()
		clean_text = clean_machine(text_read)
		clean_text = clean_text.replace("ṁ", "ṃ")
		text_list += clean_text.split()
	
	print(f"{white}{len(text_list)}")
	return text_list


bjt_text_list = make_bjt_text_list()


def make_sp_mistakes_list():
	print(f"{timeis()} {green}making spelling mistakes list", end=" ")
	sp_mistakes = pd.read_csv("../inflection generator/sandhi/spelling mistakes.csv", sep="\t", dtype=str, header=None)
	sp_mistakes_list = sp_mistakes[0].to_list()
	print(f"{white}{len(sp_mistakes_list)}")
	return sp_mistakes_list

sp_mistakes_list = make_sp_mistakes_list()

def make_variant_reading_list():
	print(f"{timeis()} {green}making variant reading list", end=" ")
	var_df = pd.read_csv("../inflection generator/sandhi/variant readings.csv", sep="\t", dtype=str, header=None)
	var_list = var_df[0].to_list()
	print(f"{white}{len(var_list)}")
	return var_list

var_list = make_variant_reading_list()

def make_sandhi_list():
	print(f"{timeis()} {green}making sandhi list", end=" ")
	sandhi_df = pd.read_csv("allwords/sandhi.csv", sep="\t", dtype=str, header=None)
	sandhi_list = sandhi_df[0].to_list()
	print(f"{white}{len(sandhi_list)}")
	return sandhi_list

sandhi_list = make_sandhi_list()

text_list = text_list + sc_text_list + bjt_text_list
text_set = set(text_list) - set(sandhi_list)
text_set = text_set - set(sp_mistakes_list)
text_set = text_set - set(var_list)
text_list = sorted(text_set, key=text_list.index)

def make_all_inflections_set():
	print(f"{timeis()} {green}making all inflections set", end=" ")
	with open("output/all inflections dict", "rb") as p:
		all_infl_dict = pickle.load(p)

	all_inflections = []
	for word in all_infl_dict:
		if all_infl_dict[word]["pos"] != "sandhix":
			all_inflections += all_infl_dict[word]["inflections"]
	
	all_inflections_set = set(all_inflections)
	print(f"{white}{len(all_inflections_set)}")
	return all_inflections_set

all_inflections_set = make_all_inflections_set()

def write_all_missing_words():
	print(f"{timeis()} {green}writing all missing words", end=" ")
	counter=0
	with open("output/allwords/missing words.csv", "w") as f:
		for word in text_list:
			if word not in all_inflections_set:
				f.write(f"{word}\n")
				counter+=1
		f.write(f"{counter}\n")
	print(f"{white}{counter}")
	

write_all_missing_words()
toc()

# (oti|āti|īti|ūti|āpi|opi|yeva|ñca|mpi|metaṃ|pissa|tveva|nti|va|ipi|upi|api|ñce|ñhi|ūpi)$

