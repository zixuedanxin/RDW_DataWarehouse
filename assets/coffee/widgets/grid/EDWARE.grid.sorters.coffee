define [
  'jquery'
  'jqGrid'
], ($, jqGrid) ->

  popBarSort = (cell, rowObject) ->
    checked = $('.inputColorBlock:checked').val()
    subject = checked.substring(0, checked.indexOf('_'))
    index = $('#' + checked ).index()
    
    for result of rowObject.results
      cur = rowObject.results[result]
      if cur.asmt_subject == subject
        value = cur.sort[index]
        break
    value
  
  popBarSort:popBarSort