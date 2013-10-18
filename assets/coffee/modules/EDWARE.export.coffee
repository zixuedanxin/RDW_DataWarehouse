define [
  "jquery"
  "mustache"
  "edwareConstants"
], ($, Mustache, Constants) ->

  class CSVBuilder
  
    constructor: (@reportType) ->

    build: (@data) ->

    getFileName: () ->
      this.reportType + '_' + new Date().getTime()


  class ISRBuilder extends CSVBuilder
  
    build: (data) ->
      'hello world'
      

  class LOSBuilder extends CSVBuilder
  
    build: (data) ->
      records = data.map (record)->
        result = []
        result.push record.name
        result.push record.results.subject1.asmt_subject
        result.push record.results.subject1.total
        result.push record.results.subject2.asmt_subject
        result.push record.results.subject2.total
        result.join Constants.DELIMITOR.COMMA
      records.join Constants.DELIMITOR.NEWLINE      


  class CPopBuilder extends CSVBuilder
  
    build: (data) ->
      records = data.map (record)->
        result = []
        result.push record.name
        result.push record.results.subject1.asmt_subject
        result.push record.results.subject1.total
        result.push record.results.subject2.asmt_subject
        result.push record.results.subject2.total
        result.join Constants.DELIMITOR.COMMA
      records.join Constants.DELIMITOR.NEWLINE

      
  builderFactory = (reportType)->
    switch reportType
      when Constants.REPORT_TYPE.CPOP then new CPopBuilder(reportType)
      when Constants.REPORT_TYPE.LOS then new LOSBuilder(reportType)
      when Constants.REPORT_TYPE.ISR then new ISRBuilder(reportType)

  download = (content, filename) ->
    uri = 'data:application/csv;charset=UTF-8,' + encodeURIComponent(content)
    link = $('<a>').html(filename).attr('href', uri).attr('download', filename)[0]
    if link.download and filename
      # have to append link to body element, or it's not gonna work in Firefox
      $('body').append link
      # download with file name
      link.click()
      $(link).remove()
    else
      # download as anonymous file
      window.open(uri, '_parent')

  exportCSV = (reportType, data) ->
    builder = builderFactory(reportType)
    download builder.build(data), builder.getFileName()


  exportCSV: exportCSV
