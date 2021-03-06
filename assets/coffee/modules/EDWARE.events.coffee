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

# module to handle all sort of events that are globally used
#
define [
  "jquery"
  "edware"
], ($, edware) ->

  # handle keyboard use highlight effect
  $('body').on
    keyup: (e) ->
      if e.keyCode is 9 # tab key
        $(this).addClass('highlight')
    mouseup: () ->
      $(this).removeClass('highlight')


  # focuslost event
  (($) ->
    currentFocusChain =$()
    focusWatch = []
    checkFocus = () ->
      newFocusChain = $(":focus").parents().andSelf()
      if newFocusChain.length isnt 0
        lostFocus = currentFocusChain.not(newFocusChain.get())
        if lostFocus.length isnt 0
          a = 0
        lostFocus.each ()->
          if $.inArray(this, focusWatch) isnt -1
            $(this).trigger('focuslost')
        currentFocusChain = newFocusChain

    $.fn.focuslost = (fn) ->
      # check both focus and blur events
      $("*", this).on 'focus blur', (e)->
        # wait until the next free loop to process focus change
        # when 'blur' is fired, focus will be unset
        setTimeout(checkFocus, 0)

      this.each () ->
        if $.inArray(this, focusWatch) is -1
          focusWatch.push this
        $(this).bind('focuslost', fn)
  )(jQuery)


  # handle click and enter keypress events
  # TODO: need refactoring
  (($) ->
    $.fn.onClickAndEnterKey = (selector, callback) ->
      # delegate click event
      $(this).on 'click', selector, callback
      # listen to enter key press event
      $(this).on 'keypress', selector, (e) ->
        callback.call(this) if e.keyCode is 13
  )(jQuery)
