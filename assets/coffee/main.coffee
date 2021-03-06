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

require {
  # version
  urlArgs: 'v1',
  baseUrl: '../js/src/',
  paths: {
    # globals
    jquery: '../3p/jquery-1.7.2.min',
    jqGrid: '../3p/jquery.jqGrid.min',
    bootstrap: '../3p/bootstrap.min',
    text: '../3p/text',
    mustache: '../3p/mustache',
    templates: '../templates',
    usmap: '../3p/usmap/jquery.usmap',
    raphael: '../3p/usmap/raphael',
    cs: '../3p/cs',
    'coffee-script': '../3p/coffee-script',

    # modules
    'Edware.LandingPage': 'modules/EDWARE.LandingPage',
    'Edware.ComparingPopulationsReport': 'modules/EDWARE.comparingPopulationsReport',
    'Edware.StudentListReport': 'modules/EDWARE.studentListReport',
    'Edware.IndividualStudentReport': 'modules/EDWARE.individualStudentReport',
    'Edware.StateMap': 'modules/EDWARE.stateMap',
    'Edware.PDFCoverSheet': 'modules/EDWARE.pdfCoverSheet',

    edware: 'modules/EDWARE',
    edwareEvents: 'modules/EDWARE.events',
    edwareContextSecurity: 'modules/EDWARE.contextSecurity',
    edwareUtil: 'modules/EDWARE.util',
    edwareConstants: 'modules/EDWARE.constants',
    edwareDataProxy: 'modules/EDWARE.dataProxy',
    edwareGrid: 'widgets/grid/EDWARE.grid.tablegrid',
    edwareGridFormatters: 'widgets/grid/EDWARE.grid.formatters',
    edwareStudentList: 'modules/EDWARE.studentList',
    edwareIndividualStudent: 'modules/EDWARE.individualStudent',
    edwareComparingPopulations: 'modules/EDWARE.comparingPopulations',
    edwareBreadcrumbs: 'widgets/breadcrumb/EDWARE.breadcrumbs',
    edwareHeader: 'widgets/header/EDWARE.header',
    edwareConfidenceLevelBar: 'widgets/confidenceLevelBar/EDWARE.confidenceBar',
    edwareLOSConfidenceLevelBar: 'widgets/losConfidenceLevelBar/EDWARE.losConfidenceBar',
    edwareClaimsBar: 'widgets/claimsBar/EDWARE.claimsBar',
    edwarePopulationBar: 'widgets/populationBar/EDWARE.populationBar',
    edwareLegend: 'widgets/legend/EDWARE.legend',
    edwareLoadingMask: 'widgets/loadingMask/EDWARE.loadingMask',
    edwareFilter: 'widgets/filter/EDWARE.filter',
    edwareClientStorage: 'widgets/clientStorage/EDWARE.clientStorage',
    edwareLanguageSelector: 'widgets/languageSelector/EDWARE.languageSelector',
    edwareGridStickyCompare: 'widgets/grid/EDWARE.grid.stickyCompare',
    edwareAsmtDropdown: 'widgets/asmtDropdown/EDWARE.asmtDropdown',
    edwarePreferences: 'modules/EDWARE.preferences',
    edwareDisclaimer: 'widgets/interimDisclaimer/EDWARE.disclaimer',
    edwareExport: 'modules/EDWARE.export',
    edwareDownload: 'widgets/download/EDWARE.download',
    edwareReportInfoBar: 'widgets/header/EDWARE.infoBar',
    edwareReportActionBar: 'widgets/header/EDWARE.actionBar',
    edwareHelpMenu: 'widgets/header/EDWARE.helpMenu',
    edwarePrint: 'widgets/print/EDWARE.print',
    edwarePrintURL: 'widgets/print/EDWARE.printURL',
    edwareRedirect: 'modules/EDWARE.stateViewRedirect',
    edwarePopover: 'widgets/popover/EDWARE.popover',
    edwareModal: 'widgets/modal/EDWARE.modal',
    edwareSearch: 'widgets/search/EDWARE.search',

    # widgets
    edwareYearDropdown: 'widgets/academicYear/EDWARE.yearDropdown',
    edwareQuickLinks: 'widgets/quickLinks/EDWARE.quickLinks',

    # templates
    edwareBreadcrumbsTemplate: 'widgets/breadcrumb/template.html',
    edwareConfidenceLevelBarTemplate: 'widgets/confidenceLevelBar/template.html',
    edwareLOSConfidenceLevelBarTemplate: 'widgets/losConfidenceLevelBar/template.html',
    edwareLOSHeaderConfidenceLevelBarTemplate: '../templates/LOS_header_perf_bar.html',
    edwarePopulationBarTemplate: 'widgets/populationBar/template.html',
    edwareClaimsBarTemplate: 'widgets/claimsBar/template.html',
    edwareAssessmentDropdownViewSelectionTemplate: '../templates/assessment_dropdown_view_selection.html',
    ISRTemplate: 'widgets/legend/ISRTemplate.html',
    CPopTemplate: 'widgets/legend/CPopTemplate.html',
    LOSTemplate: 'widgets/legend/LOSTemplate.html',
    edwareHeaderHtml: 'widgets/header/header.html',
    InfoBarTemplate: 'widgets/header/InfoBarTemplate.html',
    ActionBarTemplate: 'widgets/header/ActionBarTemplate.html',
    edwareFilterTemplate: 'widgets/filter/template.html',
    edwareDropdownTemplate: 'widgets/dropdown/template.html',
    edwareStickyCompareTemplate: 'widgets/grid/stickyCompare.template.html',
    edwareFormatterConfidenceTemplate: 'widgets/grid/ConfidenceTemplate.html',
    edwareFormatterNameTemplate: 'widgets/grid/NameTemplate.html',
    edwareFormatterPerfLevelTemplate: 'widgets/grid/PerfLevelTemplate.html',
    edwareFormatterPerformanceBarTemplate: 'widgets/grid/PerformanceBarTemplate.html',
    edwareFormatterPopulationBarTemplate: 'widgets/grid/PopulationBarTemplate.html',
    edwareFormatterSummaryTemplate: 'widgets/grid/SummaryTemplate.html',
    edwareFormatterStatusTemplate: 'widgets/grid/StatusTemplate.html',
    edwareFormatterTextTemplate: 'widgets/grid/TextTemplate.html',
    edwareFormatterTooltipTemplate: 'widgets/grid/TooltipTemplate.html',
    edwareFormatterTotalPopulationTemplate: 'widgets/grid/TotalPopulationTemplate.html',
    StateDownloadTemplate: 'widgets/download/StateDownloadTemplate.html',
    PDFOptionsTemplate: 'widgets/download/PDFOptionsTemplate.html',
    SuccessTemplate: 'widgets/download/SuccessTemplate.html',
    FailureTemplate: 'widgets/download/FailureTemplate.html',
    NoDataTemplate: 'widgets/download/NoDataTemplate.html',
    DownloadMenuTemplate: 'widgets/download/DownloadMenuTemplate.html',
    AsmtDropdownTemplate: 'widgets/asmtDropdown/template.html',
    PrintTemplate: 'widgets/print/template.html',
    HelpMenuTemplate: 'widgets/header/helpMenuTemplate.html',
    headerTemplateHtml: 'widgets/header/template.html',
    YearDropdownTemplate: 'widgets/academicYear/template.html',
    SearchBoxTemplate: 'widgets/search/SearchBoxTemplate.html',
    SearchResultTemplate: 'widgets/search/SearchResultTemplate.html',
    quickLinksTemplate: 'widgets/quickLinks/template.html',
  },
  shim: {
    'jqGrid': {
      deps: ['jquery'],
      exports: 'jqGrid'
    },
    'bootstrap': {
      deps: ['jquery'],
      exports: 'bootstrap'
    },
    'usmap': {
      deps: ['jquery', 'raphael'],
      exports: 'usmap'
    },
  }
}

(() ->
  # setup google analytics
  ((i, s, o, g, r, a, m) ->
    i['GoogleAnalyticsObject'] = r
    i[r] = i[r] || () ->
      (i[r].q = i[r].q || []).push(arguments)
    i[r].l = 1 * new Date()
    a = s.createElement(o)
    m = s.getElementsByTagName(o)[0]
    a.async = 1
    a.src = g
    m.parentNode.insertBefore(a, m)
  )(window, document, 'script', '//www.google-analytics.com/analytics.js', 'ga')

  ga('create', 'UA-43067000-1', 'edwdc.net')
  ga('send', 'pageview', {
    'page':  window.location.pathname,
    'location': window.location.protocol + "://" + window.location.host + window.location.pathname,
    'title': document.title})
)(this)
