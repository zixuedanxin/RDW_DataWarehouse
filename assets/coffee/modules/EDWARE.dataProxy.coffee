###
(c) 2014 The Regents of the University of California. All rights reserved,
subject to the license below.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.

###

define [
  'jquery'
  'mustache'
  'edwareUtil'
  'edwareLoadingMask'
  'edwarePreferences'
  'edwareConstants'
], ($, Mustache, edwareUtil, edwareLoadingMask, edwarePreferences, Constants) ->

  language = edwarePreferences.getSelectedLanguage()

  URLs =
    labels: "../data/#{language}/common/labels.json"
    filters: "../data/#{language}/filter/filter.json"
    content: "../data/#{language}/content/content.json"
    common: "../data/#{language}/common/common.json"
    landingPage: "../data/#{language}/content/landingPage.json"
    stateMap: "../data/stateMap.json"
    helpContent: "../data/#{language}/content/helpContent.json"
    pdf: "/services/pdf/indivStudentReport.html"

  # Additional data files used by specific reports
  REPORT_DATA =
    ISR: ["../data/interimAssessmentBlocks.json"]
    LOS: ["../data/interimAssessmentBlocks.json"]

  # setup URLs for report's specific JSON
  for reportName, fileName of Constants.REPORT_JSON_NAME
    URLs[fileName] = ["../data/#{language}/common/#{fileName}.json"]
    URLs[fileName] = URLs[fileName].concat(REPORT_DATA[reportName]) if REPORT_DATA[reportName]

  DEFAULT_SETTING =
    type: 'GET'
    data: ''
    async: true
    dataType: 'json'
    contentType: 'application/json'

  onError = (xhr, ajaxOptions, thrownError, redirectOnError) ->
    # Read the redirect url on 401 Unauthorized Error
    responseHeader = xhr.getResponseHeader('Content-Type')
    # redirect to login page
    if xhr.status == 401 and /application\/json/.test(responseHeader)
      return location.href = JSON.parse(xhr.responseText).redirect
    location.href = edwareUtil.getErrorPage() if redirectOnError

  getDatafromSource = (sourceURL, options) ->
    if not sourceURL || not $.type(sourceURL) in ['string', 'array']
      return new TypeError('sourceURL invalid')

    options = options || {}

    # define if redirect to error page in case error occurs on server side
    if options.hasOwnProperty('redirectOnError')
      redirectOnError = options.redirectOnError
    else
      redirectOnError = true

    config = $.extend {}, DEFAULT_SETTING
    # setup settings
    config.data = JSON.stringify options.params if options.params
    config.type = options.method if options.method

    dataLoader = edwareLoadingMask.create(context: '<div></div>')
    dataLoader.show()

    sourceURL = [ sourceURL ] if $.type(sourceURL) is 'string'
    deferreds = for url in sourceURL
      $.ajax url, config

    defer = $.Deferred()
    $.when.apply($, deferreds)
      .always ->
        $('.loader').remove()
      .done ->
        if $.type(arguments[1]) is 'string'
          # single ajax call response
          data = arguments[0]
        else
          data = {} # multiple ajax calls' response
          for args in arguments
            $.extend true, data, args[0]
        defer.resolve data
      .fail (xhr, ajaxOptions, thrownError) ->
        defer.reject arguments
        onError xhr, ajaxOptions, thrownError, redirectOnError
    defer.promise()


  getDataForReport = (reportName) ->
    reportUrl = URLs[reportName]
    reportUrl = [] if not reportUrl
    resources = [URLs.content, URLs.common, URLs.labels].concat(reportUrl)
    defer = $.Deferred()
    getDatafromSource(resources).done (data)->
      # preprocess legend data
      for key of data['legendInfo']
        data['legendInfo'][key] = data['legendInfo'][key] if data['legendInfo'].hasOwnProperty(key)
      data['legendInfo'] = JSON.parse(Mustache.render(JSON.stringify(data['legendInfo']), {'labels':data.labels}))
      defer.resolve data
    defer.promise()

  getDataForFilter = ->
    getDatafromSource [URLs.labels, URLs.filters]

  getDataForLandingPage = ->
    getDatafromSource [URLs.labels, URLs.landingPage]

  getDataForHelpContent = ->
    getDatafromSource [URLs.helpContent]

  sendBulkPDFRequest = (params) ->
    options =
      params: params
      method: 'POST'
      redirectOnError: false
      contentType: 'application/json'
    return getDatafromSource URLs.pdf, options


  getDatafromSource: getDatafromSource
  getDataForReport: getDataForReport
  getDataForFilter: getDataForFilter
  getDataForLandingPage: getDataForLandingPage
  getDataForHelpContent: getDataForHelpContent
  sendBulkPDFRequest: sendBulkPDFRequest
