import argparse
import math
import re
import shutil
import sys
from os import mkdir, walk
from os.path import basename, exists, expanduser, join, splitext
from shutil import copyfile
from subprocess import DEVNULL, check_call


"""
XML placeholders:
	name
	instrumentList
"""
XML = """<?xml version="1.0" encoding="UTF-8"?>
<drumkit_info xmlns="http://www.hydrogen-music.org/drumkit" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<name>{name}</name>
	<author></author>
	<info></info>
	<license>undefined license</license>
	<image></image>
	<imageLicense>undefined license</imageLicense>
	<componentList>
		<drumkitComponent>
			<id>0</id>
			<name>Main</name>
			<volume>1</volume>
		</drumkitComponent>
	</componentList>
	<instrumentList>
{instrumentList}
	</instrumentList>
</drumkit_info>
"""

"""
Intruments placeholders:
	id
	name
	layers
"""
INSTRUMENT = """<instrument>
	<id>{id}</id>
	<name>{name}</name>
	<volume>1</volume>
	<isMuted>false</isMuted>
	<pan_L>1</pan_L>
	<pan_R>1</pan_R>
	<randomPitchFactor>0</randomPitchFactor>
	<gain>1</gain>
	<applyVelocity>true</applyVelocity>
	<filterActive>false</filterActive>
	<filterCutoff>1</filterCutoff>
	<filterResonance>0</filterResonance>
	<Attack>0</Attack>
	<Decay>0</Decay>
	<Sustain>1</Sustain>
	<Release>1000</Release>
	<muteGroup>-1</muteGroup>
	<midiOutChannel>-1</midiOutChannel>
	<midiOutNote>60</midiOutNote>
	<isStopNote>false</isStopNote>
	<sampleSelectionAlgo>VELOCITY</sampleSelectionAlgo>
	<isHihat>-1</isHihat>
	<lower_cc>0</lower_cc>
	<higher_cc>127</higher_cc>
	<FX1Level>0</FX1Level>
	<FX2Level>0</FX2Level>
	<FX3Level>0</FX3Level>
	<FX4Level>0</FX4Level>
	<instrumentComponent>
		<component_id>0</component_id>
		<gain>1</gain>
		{layers}
	</instrumentComponent>
</instrument>
"""

"""
Layer placeholders:
	filename
	min
	max
"""
LAYER = """<layer>
	<filename>{filename}</filename>
	<min>{min}</min>
	<max>{max}</max>
	<gain>1</gain>
	<pitch>0</pitch>
</layer>
"""

hydrogen_path = expanduser('~/.hydrogen/data/drumkits')
interleave = 1 / 3


def create_folder(name):
	path = join(hydrogen_path, name)
	try:
		mkdir(path)
	except FileExistsError:
		pass
	except Exception as e:
		sys.exit(str(e))
	return path


def get_files(files, extension, layers=None):
	files = sorted([f for f in files if splitext(f)[-1] == extension])
	if layers:
		samples = len(files)
		if samples > layers:
			delta = samples / layers
			files = [files[math.floor(delta * i) - 1] for i in range(1, layers + 1)]
	return files


def normalize(text):
	return re.sub('[\W]+', '', text)


def process_files(root, files, path, output_format):
	for file in files:
		print('Processing %s...' % file)
		destination = join(path, file)
		if output_format:
			destination = splitext(destination)[0] + '.' + output_format
		if exists(destination):
			continue
		source = join(root, file)
		if output_format:
			check_call(['sox', source, destination], stdout=DEVNULL)
		else:
			copyfile(source, destination)


def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('folder', help='folder containing the samples')
	parser.add_argument('name', help='name of the drumkit')
	parser.add_argument(
		'--layers',
		default=16,
		help='max layers per instrument (default: 16)',
		type=int)

	parser.add_argument(
		'--from',
		choices=['flac', 'wav'],
		default='wav',
		dest='input_format',
		help='file format to look for (default: wav)')
	parser.add_argument(
		'--to',
		choices=['flac', 'wav'],
		dest='output_format',
		help='output file format (requires SoX)')

	return parser.parse_args()


def main():
	args = parse()
	name = args.name
	layers = args.layers
	samples_path = args.folder
	drumkit_path = create_folder(name)
	input_format = args.input_format
	output_format = args.output_format

	# Check for SoX if necessary.
	if output_format and not shutil.which('sox'):
		sys.exit('error: sox not found! Can\'t convert to %s' % output_format)

	extension = '.' + input_format

	id = 0
	instruments_xml = ''
	for root, dirs, files in walk(samples_path, topdown=False):
		if files:
			# Filter FLAC files.
			files = get_files(files, extension, layers)
			samples = len(files)

			if samples == 0:
				continue

			process_files(root, files, drumkit_path, output_format)

			# Compute position and length in layer.
			length = (1 / samples) * (1 + (interleave / 2))
			offset = (1 - length) / (samples - 1)

			layers_xml = ''
			for i, file in enumerate(files):
				min = i * offset
				max = min + length
				layers_xml += LAYER.format(
					filename=basename(file),
					min=min,
					max=max)
			instrument_xml = INSTRUMENT.format(
				id=id,
				name=normalize(root),
				layers=layers_xml)
			id = id + 1
			instruments_xml += instrument_xml
	xml = XML.format(name=name, instrumentList=instruments_xml)

	# If no files were found...
	if id == 0:
		sys.exit('error: no files found')

	print('Writting XML...')
	xml_path = join(drumkit_path, 'drumkit.xml')
	with open(xml_path, 'w') as xml_file:
		xml_file.write(xml)
	print('Done.')


main()
