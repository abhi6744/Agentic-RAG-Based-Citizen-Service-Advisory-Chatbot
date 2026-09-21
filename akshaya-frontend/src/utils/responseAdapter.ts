export function normalizeChatResponse(data: any): any {
  let summary = "";
  let answer = data.answer || {};

  if (answer.summary) {
    summary = answer.summary.trim();
  } else if (data.summary) {
    summary = data.summary.trim();
  }

  if (!summary) {
    summary = "I could not generate a clear summary for this response. Please review the verified sections below or try rephrasing your question.";
  }

  if (data.success === false && data.status === "image_analysis_failed") {
    summary = answer.summary || "I could not evaluate this image right now. Please upload a clearer document image or describe your question in text.";
  }

  return {
    ...data,
    success: data.success !== false,
    status: data.status || "grounded_answer",
    answer: {
      ...answer,
      summary
    }
  };
}
