using Stateless;
using Stateless.Graph;
using System;
using System.Collections.Generic;
using System.Text;

namespace NPS.Workflow.Workflows.ERB
{
    public partial class ERBReview<T>
    {
        private StateMachine<State, Trigger> _machine;

        private T _context;

        StateMachine<State, Trigger>.TriggerWithParameters<Reviewer> _approvedTrigger;
        StateMachine<State, Trigger>.TriggerWithParameters<Reviewer> _approvedWithSuggestionsTrigger;
        StateMachine<State, Trigger>.TriggerWithParameters<Reviewer> _additionalReviwReqdTrigger;
        StateMachine<State, Trigger>.TriggerWithParameters<Reviewer> _notApprovedTrigger;

        public static ERBReview<T> Create(T context) {
            return new ERBReview<T>(context);
        }

        public State State
        {
            get { return _machine.State; }
        }

        private ERBReview(T context)
        {
            _context = context;
            _machine = new StateMachine<State, Trigger>(State.Start);
            Configure();
        }

        #region Triggers
        public void Assign()
        {
            _machine.Fire(Trigger.Assign);
        }

        public void Approve(Reviewer reviewer) {
            _machine.Fire(_approvedTrigger, reviewer);
        }

        public void Deny(Reviewer reviewer)
        {
            _machine.Fire(_notApprovedTrigger, reviewer);
        }

        #endregion

        #region Event handlers
        public void OnReviewStart()
        {
            Console.WriteLine("Review process started...");
        }

        public void OnDivisionReviewStart()
        {
            Console.WriteLine("Division Review process started...");
        }

        public void OnOUReviewStart()
        {
            Console.WriteLine("OUReview Review process started...");
        }
        public void OnERBReviewStart()
        {
            Console.WriteLine("ERBReview Review process started...");
        }

        public void OnERBBoardStart()
        {
            Console.WriteLine("ERBBoard Review process started...");
        }
        
        public void OnNotApproved(Reviewer reviewer)
        {
            Console.WriteLine("NOT approved.");
        }

        public void OnApproved(Reviewer reviewer)
        {
            Console.WriteLine("APPROVED.");
        }

        public void OnApprovedWithSuggestions(Reviewer reviewer)
        {
            Console.WriteLine("APPROVED with suggestions.");
        }

        public void OnNeedsAdditionalReview2(Reviewer reviewer, Transition t)
        {
            Console.WriteLine("Needs additional review.");
        }

        public void OnNeedsAdditionalReview(Reviewer reviewer)
        {
            Console.WriteLine("Needs additional review.");
        }
        #endregion

        #region Conditionals
        public bool CanGoInERBBoard(State current)
        {
            return false;
        }

        public bool CanGoInOtherReview(State current)
        {
            return true;
        }

        public bool CanGoInERBReview(State current)
        {
            return false;
        }

        public bool CanGoInOUReview(State current)
        {
            return true;
        }
        #endregion
    }
}
