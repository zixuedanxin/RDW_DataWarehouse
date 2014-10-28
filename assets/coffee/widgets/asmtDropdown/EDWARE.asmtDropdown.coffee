define [
  "jquery"
  "mustache"
  "text!AsmtDropdownTemplate"
  "edwarePreferences"
  "edwareEvents"
  "edwareConstants"
], ($, Mustache, AsmtDropdownTemplate, edwarePreferences, edwareEvents, Constants) ->

  class EdwareAsmtDropdown

    constructor: (@container, @config, @getAsmtPreference, @callbacks) ->
      @displayTemplate = @config.asmtSelectorTemplate
      @dropdownValues = @getAsmtTypes()
      @initialize()
      @setDefaultOption()
      @bindEvents()

    initialize: () ->
      currentYear = edwarePreferences.getAsmtYearPreference()
      latestYear = []
      otherYears = []
      for v in @dropdownValues
        if v.asmt_period_year is currentYear
          latestYear.push v
        else
          otherYears.push v

      years = []
      if @config.years
        for year in @config.years
          if year.value isnt currentYear
            years.push year

      output = Mustache.to_html AsmtDropdownTemplate,
        latestYear: latestYear
        otherYears: otherYears
        hasOtherYears: otherYears.length > 0
        academicYears: years
        hasOtherAcademicYears: years.length > 0
      @container.html(output)

    getAsmtTypes: () ->
      asmtTypes = []
      for idx, asmt of @config.asmtTypes
        asmt.asmt_year = asmt.effective_date.substr(0, 4) if asmt.effective_date
        asmt.asmt_type = Constants.ASMT_TYPE[asmt.asmt_type]
        asmt.display = @getAsmtDisplayText(asmt)
        asmtTypes.push asmt
      asmtTypes

    setDefaultOption: () ->
      # set default option, comment out for now
      asmt = @getAsmtPreference() #edwarePreferences.getAsmtPreference()
      if $.isEmptyObject(asmt)
        # set first option as default value
        asmt = @parseAsmtInfo $('.asmtSelection')
        edwarePreferences.saveAsmtPreference asmt
        edwarePreferences.saveAsmtForISR asmt
      @setSelectedValue asmt

    bindEvents: () ->
      self = this
      $(@container).onClickAndEnterKey '.asmtSelection', ->
        asmt = self.parseAsmtInfo $(this)
        self.setSelectedValue asmt
        # additional parameters
        self.callbacks.onAsmtYearSelected(asmt)

      $(@container).onClickAndEnterKey '.asmtYearButton', ->
        value = $(this).data('value')
        edwarePreferences.saveAsmtYearPreference(value)
        self.callbacks.onAcademicYearSelected value

      # collapse dropdown menu when focus out
      $('.btn-group', @container).focuslost ->
        $(this).removeClass('open')

    parseAsmtInfo: ($option) ->
      display: $option.data('display')
      asmt_type: $option.data('asmttype')
      asmt_guid: $option.data('asmtguid')?.toString()
      effective_date: $option.data('effectivedate')
      asmt_grade: $option.data('grade')
      asmt_period_year: $option.data('asmtperiodyear')

    setSelectedValue: (asmt) ->
      displayText = @getAsmtDisplayText(asmt)
      $('#selectedAsmtType').html displayText
      # show iab message
      $IABMessage =  $(".IABMessage")
      grade = @config.grade
      if asmt?.asmt_type is Constants.ASMT_TYPE.IAB and grade
        $('.grade', ".IABMessage").html grade?.id
        $IABMessage.show()
      else
        $IABMessage.hide()

    getAsmtDisplayText: (asmt)->
      # Format for interim blocks is different
      if asmt.asmt_type is Constants.ASMT_TYPE['INTERIM ASSESSMENT BLOCKS']
        asmt.asmt_from_year = asmt.asmt_period_year - 1
        asmt.asmt_to_year = asmt.asmt_period_year
        return Mustache.to_html @displayTemplate[asmt.asmt_type], asmt
      return "" if not asmt.effective_date
      effective_date = asmt.effective_date.toString()
      asmt.asmt_year = effective_date.substr(0, 4)
      asmt.asmt_month = effective_date.substr(4, 2)
      asmt.asmt_day = effective_date.substr(6, 2)
      Mustache.to_html @displayTemplate['default'], asmt

  # dropdownValues is an array of values to feed into dropdown
  (($)->
    $.fn.edwareAsmtDropdown = (config, getAsmtPreference, callbacks) ->
      new EdwareAsmtDropdown($(this), config, getAsmtPreference, callbacks)
  ) jQuery

  EdwareAsmtDropdown: EdwareAsmtDropdown
