# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Polygon People Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Samweli Twesa Mwakisambwe "Samweli" <smwltwesa6@gmail.com>'
__date__ = '13/10/15'

from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.impact_reports.report_mixin_base import ReportMixin

from safe.common.utilities import format_int
from safe.impact_functions.core import evacuated_population_needs
from safe.gui.tools.minimum_needs.needs_profile import filter_needs_parameters
from safe.impact_functions.core import population_rounding


class PolygonPeopleExposureReportMixin(ReportMixin):
    """Population specific report.
    """

    def __init__(self):
        """Area specific report mixin.

        .. versionadded:: 3.2

        """
        self._question = ''
        self._areas = {}
        self._affected_areas = {}
        self._areas_population = {}
        self._total_population = 0
        self._unaffected_population = 0
        self._affected_population = {}
        self._other_population_counts = {}
        self._minimum_needs = []

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        question = self.question
        impact_summary = self.impact_summary()
        breakdown = self.breakdown()
        minimum_needs = self.total_needs.copy()
        action_checklist = self.action_checklist()
        notes = self.notes()

        return {
            'exposure': 'polygon people',
            'question': question,
            'impact summary': impact_summary,
            'breakdown': breakdown,
            'minimum needs': minimum_needs,
            'action check list': action_checklist,
            'notes': notes
        }

    def impact_summary(self):
        """Create impact summary as data.

        :returns: Impact Summary in dictionary format.
        :rtype: dict
        """
        attributes = ['category', 'value']
        fields = []

        for key, value in self.hazard_levels.iteritems():
            name = self.hazard_class_mapping[key][0]
            # This skips reporting people not affected in No zone
            if key == 'wet':
                row = []
                row.append(tr(
                    'People within hazard field ("%s") of value "%s"')
                               % (self.hazard_class_field, name))
                row.append(value)
            elif key == 'dry':
                continue
            else:
                row = []
                row.append(name)
                row.append(value)
            fields.append(row)

        # Total affected population
        fields.append(
            [tr('Total affected people'), self.total_affected_population])
        # Non affected population
        fields.append([tr('Unaffected people'), self.unaffected_population])
        # Total Population
        fields.append([tr('Total people'), self.total_population])

        return {
            'attributes': attributes,
            'fields': fields
        }

    def action_checklist(self):
        """Return the action check list section of the report.

        :return: The action check list as dict.
        :rtype: dict
        """
        title = tr('Action checklist')

        population = population_rounding(
            sum(self.affected_population.values()))

        fields = [
            tr('Which group or people is most affected?'),
            tr('Who are the vulnerable people in the population and why?'),
            tr('How will warnings be disseminated?'),
            tr('What are people\'s likely movements?'),
            tr('What are the security factors for the affected people?'),
            tr('What are the security factors for relief responders?'),
            tr('How will we reach evacuated people?'),
            tr('What kind of food does the people normally consume?'),
            tr('What are the critical non-food items required by the affected '
               'people?'),
            tr('Are there enough water supply, sanitation, hygiene, food, '
               'shelter, medicines and relief items available for %s people?'
                % format_int(population)),
            tr('If yes, where are they located and how will we distribute '
               'them?'),
            tr('If no, where can we obtain additional relief items and how '
               'will we distribute them?'),
            tr('What are the related health risks?'),
            tr('Who are the key people responsible for coordination?')
        ]

        return {
            'title': title,
            'fields': fields
        }

    @property
    def total_needs(self):
        """Get the total minimum needs based on the total evacuated.

        :returns: Total minimum needs.
        :rtype: dict
        """
        total_population_evacuated = sum(self.affected_population.values())
        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        return evacuated_population_needs(
            total_population_evacuated, self.minimum_needs)

    def breakdown(self):
        """Create breakdown as data.

        :returns: Breakdown in dictionary format.
        :rtype: dict
        """
        attributes = [
            tr('Area Name'),
            tr('Affected Area (ha)'),
            tr('Affected Area (%)'),
            tr('Total (ha)'),
            tr('Affected People'),
            tr('Affected People(%)'),
            tr('Total Number of People'),
        ]

        fields = []

        areas = self.areas
        affected_areas = self.affected_areas
        for area_id, value in areas.iteritems():
            if area_id in affected_areas:
                affected = affected_areas[area_id]
            else:
                affected = 0.0
            single_total_area = value

            if value:
                affected_area_ratio = affected / single_total_area
            else:
                affected_area_ratio = 0.0
            percent_affected = affected_area_ratio * 100
            percent_affected = round(percent_affected, 1)
            number_people_affected = (
                affected_area_ratio * self.areas_population[area_id])

            # rounding to float without decimal, we can't have number
            #  of people with decimal
            number_people_affected = round(number_people_affected, 0)

            if self.areas_population[area_id] != 0:
                percent_people_affected = (
                    (number_people_affected / self.areas_population[area_id]) *
                    100)
            else:
                percent_people_affected = 0
            affected *= 1e8
            single_total_area *= 1e8

            fields.append([
                self.area_name(area_id),
                affected,
                percent_affected,
                single_total_area,
                number_people_affected,
                percent_people_affected,
                self.areas_population[area_id]
            ])

        return {
            'attributes': attributes,
            'fields': fields
        }

    @property
    def affected_population(self):
        """Get the affected population counts.

        :returns: Affected population counts.
        :rtype: dict
        """
        if not hasattr(self, '_affected_population'):
            self._affected_population = OrderedDict()
        return self._affected_population

    @affected_population.setter
    def affected_population(self, affected_population):
        """Set the affected population counts.
        :param affected_population: The population counts.
        :type affected_population: dict
        """
        self._affected_population = affected_population

    @property
    def question(self):
        """Get the impact function question.

        :returns: The impact function question.
        :rtype: basestring
        """
        if not hasattr(self, '_question'):
            self._question = ''
        return self._question

    @question.setter
    def question(self, question):
        """Set the impact function question.

        :param question: The question.
        :type question: basestring
        """
        self._question = question

    @property
    def unaffected_population(self):
        """Get the unaffected population count.

        :returns: The unaffected population count.
        :returns: int
        """
        if not hasattr(self, '_unaffected_population'):
            self._unaffected_population = 0
        return self._unaffected_population

    @unaffected_population.setter
    def unaffected_population(self, unaffected_population):
        """Set the unaffected population count.

        :param unaffected_population: The unaffected population count.
        :return: int
        """
        self._unaffected_population = unaffected_population

    @property
    def affected_areas(self):
        """Get the affected areas.

        :returns: affected areas.
        :rtype: {}.
        """
        return self._affected_areas

    @affected_areas.setter
    def affected_areas(self, affected_areas):
        """Set the affected areas.

        :param affected_areas: affected areas.
        :type affected_areas:dict
        """
        self._affected_areas = affected_areas

    @property
    def total_affected_areas(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.affected_areas.values())

    @property
    def areas_population(self):
        """Get the areas population.

        :returns: areas population.
        :rtype: dict.
        """
        return self._areas_population

    @areas_population.setter
    def areas_population(self, areas_population):
        """Set the areas population.

        :param areas_population: area population.
        :type areas_population:dict
        """
        self._areas_population = areas_population

    @property
    def total_areas_population(self):
        """Get the total affected areas.

        :returns: Total affected areas.
        :rtype: int.
        """
        return sum(self.areas_population.values())

    @property
    def total_areas(self):
        """Get the total area.

        :returns: Total area.
        :rtype: int.
        """
        return sum(self.areas.values())

    @property
    def areas(self):
        """Get the areas.

        :returns: areas.
        :rtype: dict.
        """
        return self._areas

    @areas.setter
    def areas(self, areas):
        """Set the areas.

        :param areas.
        :type areas: dict
        """
        self._areas = areas

    @property
    def total_affected_population(self):
        """Get the total affected population.

        :returns: Total affected population.
        :rtype: int.
        """
        return sum(self.affected_population.values())

    @property
    def total_population(self):
        """Get the total population.

        :returns: The total population.
        :rtype: int
        """
        if not hasattr(self, '_total_population'):
            self._total_population = 0
        return self._total_population

    @total_population.setter
    def total_population(self, total_population):
        """Set the total population.

        :param total_population: The total population count.
        :type total_population: int
        """
        self._total_population = total_population

    def area_name(self, area_id):
        """ Return the name of area.

        :param area_id: area id.
        :type area_id: int

        :returns area_name: name of the area
        :rtype area_name: string
        """

        area_name = self.areas_names[area_id]

        return area_name

    @property
    def minimum_needs(self):
        """Get the minimum needs as specified, or default.

        :returns: The minimum needs parameters.
        :rtype: list
        """
        if not hasattr(self, '_minimum_needs'):
            self._minimum_needs = []
        return self._minimum_needs

    @minimum_needs.setter
    def minimum_needs(self, minimum_needs):
        """Set the minimum needs parameters list.

        :param minimum_needs: Minimum needs
        :type minimum_needs: list
        """
        self._minimum_needs = minimum_needs
