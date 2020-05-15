// Copyright 2019 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Service for fetching the opportunities available for
 * contributors to contribute.
 */

import { downgradeInjectable } from '@angular/upgrade/static';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { ExplorationOpportunitySummary, ITranslationCountsDict } from
  'domain/opportunity/ExplorationOpportunitySummaryObjectFactory';
import { IFetchedExplorationOpportunitiesSuccessCallbackParams,
  IFetchedSkillOpportunitiesSuccessCallbackParams } from
  './contribution-opportunities.service';
import { SkillOpportunity } from
  'domain/opportunity/SkillOpportunityObjectFactory';
import { UrlInterpolationService } from
  'domain/utilities/url-interpolation.service';

const constants = require('constants.ts');

type ContributionOpportunityCategoryType =
  'skill' | 'voiceover' | 'translation';

type ContributionOpportunityParams = {
  cursor: string;
  // eslint-disable-next-line camelcase
  language_code?: string;
};

export interface IOpportunityDict {
  id: string
  // eslint-disable-next-line camelcase
  topic_name: string
  // eslint-disable-next-line camelcase
  story_title: string
  // eslint-disable-next-line camelcase
  chapter_title: string
  // eslint-disable-next-line camelcase
  skill_description?: string
  // eslint-disable-next-line camelcase
  content_count: number
  // eslint-disable-next-line camelcase
  translation_counts?: ITranslationCountsDict
  // eslint-disable-next-line camelcase
  question_count?: number
}

@Injectable({
  providedIn: 'root'
})
export class ContributionOpportunitiesBackendApiService {
  urlTemplate = '/opportunitiessummaryhandler/<opportunityType>';
  constructor(private urlInterpolationService: UrlInterpolationService,
    private http: HttpClient) { }

  // TODO(#7165): Replace any with exact type.
  private _getOpportunityFromDict(
      opportunityType: ContributionOpportunityCategoryType,
      opportunityDict: IOpportunityDict
  ): ExplorationOpportunitySummary | SkillOpportunity {
    if (
      opportunityType === constants.OPPORTUNITY_TYPE_VOICEOVER ||
      opportunityType === constants.OPPORTUNITY_TYPE_TRANSLATION) {
      return new ExplorationOpportunitySummary(opportunityDict.id,
        opportunityDict.topic_name, opportunityDict.story_title,
        opportunityDict.chapter_title, opportunityDict.content_count,
        opportunityDict.translation_counts);
    } else if (opportunityType === constants.OPPORTUNITY_TYPE_SKILL) {
      return new SkillOpportunity(
        opportunityDict.id, opportunityDict.skill_description,
        opportunityDict.topic_name, opportunityDict.question_count);
    }
  }

  // TODO(#7165): Replace any with exact type.
  private _fetchOpportunities(
      opportunityType: ContributionOpportunityCategoryType,
      params: ContributionOpportunityParams,
      successCallback:
        (value: IFetchedExplorationOpportunitiesSuccessCallbackParams |
          IFetchedSkillOpportunitiesSuccessCallbackParams) => void,
      errorCallback: (reason?: any) => void): void {
    this.http.get(this.urlInterpolationService.interpolateUrl(
      this.urlTemplate, { opportunityType }
    ), { params }).toPromise().then((data: any) => {
      const opportunities = [];
      for (const index in data.opportunities) {
        opportunities.push(this._getOpportunityFromDict(
          opportunityType, data.opportunities[index]));
      }
      if (successCallback) {
        const result = {
          opportunities: opportunities,
          nextCursor: data.next_cursor,
          more: data.more
        };
        successCallback(result);
      }
    }, (error) => {
      if (errorCallback) {
        errorCallback(error);
      }
    });
  }

  fetchSkillOpportunities(cursor: string): Promise<Object> {
    const params: ContributionOpportunityParams = {
      cursor: cursor
    };
    return new Promise((resolve, reject) => {
      this._fetchOpportunities(
        constants.OPPORTUNITY_TYPE_SKILL, params, resolve, reject);
    });
  }

  fetchTranslationOpportunities(languageCode: string, cursor: string):
    Promise<Object> {
    const params: ContributionOpportunityParams = {
      language_code: languageCode,
      cursor: cursor
    };
    return new Promise((resolve, reject) => {
      this._fetchOpportunities(
        constants.OPPORTUNITY_TYPE_TRANSLATION,
        params, resolve, reject);
    });
  }

  fetchVoiceoverOpportunities(languageCode: string,
      cursor: string): Promise<Object> {
    const params: ContributionOpportunityParams = {
      language_code: languageCode,
      cursor: cursor
    };
    return new Promise((resolve, reject) => {
      this._fetchOpportunities(
        constants.OPPORTUNITY_TYPE_VOICEOVER,
        params, resolve, reject);
    });
  }
}

angular.module('oppia').factory(
  'ContributionOpportunitiesBackendApiService',
  downgradeInjectable(ContributionOpportunitiesBackendApiService));
