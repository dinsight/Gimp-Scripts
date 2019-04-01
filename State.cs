using System;
using System.Collections.Generic;
using System.Text;

namespace NPS.Workflow.Workflows.ERB
{
    public enum State
    {
        Start,
        DivisionReview,
        OUReview,
        ERBReview,
        OtherReviews,
        ERBBoard,
        End
    }
}
