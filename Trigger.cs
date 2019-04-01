using System;
using System.Collections.Generic;
using System.Text;

namespace NPS.Workflow.Workflows.ERB
{
    public enum Trigger
    {
        Assign,
        Approved,
        ApprovedWithSuggestions,
        AdditionalReviewRequired,
        NotApproved
    }
}
