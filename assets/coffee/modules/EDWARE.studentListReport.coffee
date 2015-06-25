require [
  "edwareStudentList"
  "edwareDataProxy"
  "edwareConstants"
  "edwarePreferences"
  "edwareUtil"
], (edwareStudentList, edwareDataProxy, Constants, edwarePreferences, edwareUtil) ->

  reportName = Constants.REPORT_JSON_NAME.LOS

  # load LOS configuration data
  edwareDataProxy.getDataForReport(reportName).done (config) ->
    studentGrid = new edwareStudentList.StudentGrid(config)
    params = edwareUtil.getUrlParams()
    params = mergeWithPreference(params)
    studentGrid.reload params

  mergeWithPreference = (params)->
    edwarePreferences.saveStateCode(params['stateCode'])
    asmtYear = edwarePreferences.getAsmtYearPreference()
    asmtType = edwarePreferences.getAsmtType()
    params['asmtYear'] = asmtYear if asmtYear
    # if asmtType
    #   params.asmtType = asmtType.toUpperCase()
    # else
    #   params.asmtType = Constants.ASMT_TYPE.SUMMATIVE.toUpperCase()
    params.asmtType = Constants.ASMT_TYPE.SUMMATIVE.toUpperCase()
    params
