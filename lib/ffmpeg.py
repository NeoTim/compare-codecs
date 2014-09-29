"""Framework for specifying encoders from ffmpeg.

This uses ffmpeg for encoding and decoding.
The default FFMPEG encoder uses mpeg4, so that we can see if it's roughly
compatible with the vpxenc-produced qualities.
"""
import ast
import os
import subprocess

import encoder
import file_codec

class FfmpegCodec(file_codec.FileCodec):
  def __init__(self, name='ffmpeg-mpeg4'):
    # Subclasses need to override name, codecname and extension.
    # At the moment, no parameters are defined.
    self.name = name
    self.codecname = 'mpeg4'
    self.extension = 'avi'
    super(FfmpegCodec, self).__init__(name)

  def StartEncoder(self):
    return encoder.Encoder(self, encoder.OptionValueSet(self.option_set, ''))

  def EncodeCommandLine(self, parameters, bitrate, videofile, encodedfile):
    commandline = (
      '%s %s -s %dx%d -i %s -codec:v %s -b:v %dk -y %s' % (
        encoder.Tool('ffmpeg'),
        parameters.ToString(), videofile.width, videofile.height,
        videofile.filename, self.codecname,
        bitrate, encodedfile))
    return commandline

  def DecodeCommandLine(self, videofile, encodedfile, yuvfile):
    commandline = "%s -codec:v %s -i %s %s" % (
      encoder.Tool('ffmpeg'),
      self.codecname,
      encodedfile, yuvfile)
    return commandline

  def ResultData(self, encodedfile):
    commandline = '%s -show_frames -of json %s' % (encoder.Tool('ffprobe'),
                                                   encodedfile)
    ffprobeinfo = subprocess.check_output(commandline, shell=True)
    probeinfo = ast.literal_eval(ffprobeinfo)
    pos = 0
    frameinfo = []
    for frame in probeinfo['frames']:
      if pos != 0:
        frameinfo.append({'size': 8*(int(frame['pkt_pos']) - pos)})
      pos = int(frame['pkt_pos'])
    frameinfo.append({'size': 8*(os.path.getsize(encodedfile) - pos)})
    return {'frame': frameinfo}