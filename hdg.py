import argparse
import math
import re
import shutil
import sys
from os import makedirs, walk
from os.path import basename, exists, expanduser, join, sep, splitext
from shutil import copyfile
from subprocess import DEVNULL, check_call
from sys import platform


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

if platform == "darwin":
	hydrogen_path = '~/Library/Application Support/Hydrogen'
else:
	hydrogen_path = '~/.hydrogen'

hydrogen_path = expanduser(hydrogen_path)
drumkits_path = join(hydrogen_path, 'data/drumkits')

layers_interleaving = 1 / 3  # Interleave layers by their third.


def copy_files(root, files, drumkit_path, output_format=None):
	"""Copy the samples into the drum kit."""
	for file in files:
		print('Processing %s...' % file)
		destination = join(drumkit_path, file)
		# Change extension if output format is different.
		if output_format:
			destination = '.'.join((splitext(destination)[0], output_format))
		if not exists(destination):
			source = join(root, file)
			if output_format:
				check_call(['sox', source, destination], stdout=DEVNULL)
			else:
				copyfile(source, destination)
		yield destination


def get_drumkit_path(name):
	"""Create and return the folder of the drum kit."""
	path = join(drumkits_path, name)
	if not exists(path):
		try:
			makedirs(path)
		except Exception as e:
			sys.exit('error: cannot create drum kit folder (%s)' % str(e))
	return path


def pick_files(files, extension, layers=None):
	"""Pick samples from a list of samples."""
	# Filter by extension.
	files = list(filter(lambda f: splitext(f)[-1] == extension, files))
	# If number of layers set, pick samples in list.
	if layers:
		samples = len(files)
		# Use a linear interpolation to select the samples.
		if samples > layers:
			delta = samples / layers
			files_range = range(1, layers + 1)
			files = [files[math.floor(delta * i) - 1] for i in files_range]
	# Sort by natural order.
	if files:
		# Get length of longest name in list.
		length = len(max(files, key=len))
		# Sort list by natural order by padding with 0s all short names.
		files.sort(key=lambda x: x.rjust(length, '0'))
	return files


def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('folder', help='folder containing the samples')
	parser.add_argument('name', help='name of the drum kit')
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
	# Check for Hydrogen folder.
	if not exists(hydrogen_path):
		sys.exit('error: cannot find Hydrogen data (%s)' % hydrogen_path)

	args = parse()
	name = args.name
	layers = args.layers
	samples_path = args.folder
	drumkit_path = get_drumkit_path(name)
	input_format = args.input_format
	output_format = args.output_format

	# Check for SoX if necessary.
	if output_format and not shutil.which('sox'):
		sys.exit('error: sox not found (needed for format conversion)')

	input_extension = '.' + input_format

	# Generate XML...
	instrument_id = 0
	instruments_xml = ''
	instrument_name_offset = len(samples_path)
	for root, dirs, files in walk(samples_path, topdown=False):
		if not files:
			continue

		files = pick_files(files, input_extension, layers)

		samples = len(files)
		if samples == 0:
			continue

		files = copy_files(root, files, drumkit_path, output_format)

		# Compute length and offset of layers.
		length = (1 / samples) * (1 + layers_interleaving)
		offset = (1 - length) / (samples - 1)

		# Generate current instrument.
		layers_xml = ''
		instrument_name = re.sub(sep, ' ', root[instrument_name_offset:])
		for i, file in enumerate(files):
			min = i * offset
			layers_xml += LAYER.format(
				filename=basename(file),
				min=min,
				max=min + length)
		instrument_xml = INSTRUMENT.format(
			id=instrument_id,
			name=instrument_name,
			layers=layers_xml)
		instrument_id = instrument_id + 1
		instruments_xml += instrument_xml
	xml = XML.format(name=name, instrumentList=instruments_xml)

	# If no files were found...
	if instrument_id == 0:
		sys.exit('error: no files found')

	print('Writting XML...')
	xml_path = join(drumkit_path, 'drumkit.xml')
	with open(xml_path, 'w') as xml_file:
		xml_file.write(xml)
	print('Done.')


main()
