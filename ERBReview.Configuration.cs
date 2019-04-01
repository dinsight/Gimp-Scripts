using System;
using System.Collections.Generic;
using System.Text;

namespace NPS.Workflow.Workflows.ERB
{
    public partial class ERBReview<T>
    {
        private void Configure()
        {
            _approvedTrigger = _machine.SetTriggerParameters<Reviewer>(Trigger.Approved);
            _approvedWithSuggestionsTrigger = _machine.SetTriggerParameters<Reviewer>(Trigger.ApprovedWithSuggestions);
            _additionalReviwReqdTrigger = _machine.SetTriggerParameters<Reviewer>(Trigger.AdditionalReviewRequired);
            _notApprovedTrigger = _machine.SetTriggerParameters<Reviewer>(Trigger.NotApproved);

            _machine.Configure(State.Start)
                .OnEntry(OnReviewStart)
                .Permit(Trigger.Assign, State.DivisionReview);

            _machine.Configure(State.DivisionReview)
                .OnEntry(OnDivisionReviewStart)
                .PermitIf(_approvedTrigger, State.OUReview, (reviewer) => CanGoInOUReview(_machine.State))
                .PermitIf(_approvedTrigger, State.ERBReview, (reviewer) => CanGoInERBReview(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.OUReview, (reviewer) => CanGoInOUReview(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.ERBReview, (reviewer) => CanGoInERBReview(_machine.State))
                .InternalTransition(_additionalReviwReqdTrigger, (reviewer, transition) => OnNeedsAdditionalReview(reviewer))
                .PermitIf(_notApprovedTrigger, State.End);
            
            _machine.Configure(State.OUReview)
                .OnEntry(OnOUReviewStart)
                .PermitIf(_approvedTrigger, State.ERBReview)
                .PermitIf(_approvedWithSuggestionsTrigger, State.ERBReview, (x) => CanGoInERBBoard(_machine.State))
                .InternalTransition(_additionalReviwReqdTrigger, (reviewer, transition) => OnNeedsAdditionalReview(reviewer))
                .PermitIf(_notApprovedTrigger, State.End);

            _machine.Configure(State.ERBReview)
                .OnEntry(OnERBReviewStart)
                .PermitIf(_approvedTrigger, State.OtherReviews, (x)=>CanGoInOtherReview(_machine.State))
                .PermitIf(_approvedTrigger, State.ERBBoard, (x)=>CanGoInERBBoard(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.OtherReviews, (x) => CanGoInOtherReview(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.ERBBoard, (x) => CanGoInERBBoard(_machine.State))
                .InternalTransition(_additionalReviwReqdTrigger, (reviewer, transition) => OnNeedsAdditionalReview(reviewer))
                .PermitIf(_notApprovedTrigger, State.End);

            _machine.Configure(State.OtherReviews)
                .OnEntry(OnERBReviewStart)
                .PermitIf(_approvedTrigger, State.ERBBoard, (x) => CanGoInERBBoard(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.ERBBoard, (x) => CanGoInERBBoard(_machine.State))
                .InternalTransition(_additionalReviwReqdTrigger, (reviewer, transition) => OnNeedsAdditionalReview(reviewer))
                .PermitIf(_notApprovedTrigger, State.End);

            _machine.Configure(State.ERBBoard)
                .OnEntry(OnERBBoardStart)
                .PermitIf(_approvedTrigger, State.End, (x) => CanGoInERBBoard(_machine.State))
                .PermitIf(_approvedWithSuggestionsTrigger, State.End, (x) => CanGoInERBBoard(_machine.State))
                .InternalTransition(_additionalReviwReqdTrigger, (reviewer, transition) => OnNeedsAdditionalReview(reviewer))
                .PermitIf(_notApprovedTrigger, State.End);

            _machine.Configure(State.End)
                .OnEntryFrom(_approvedTrigger, OnApproved, null)
                .OnEntryFrom(_approvedWithSuggestionsTrigger, OnApprovedWithSuggestions, null)
                .OnEntryFrom(_notApprovedTrigger, OnNotApproved, null)
                .OnExit(x=> { });
        }
    }
}
