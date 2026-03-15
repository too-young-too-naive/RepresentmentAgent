import { useState, useCallback, useRef } from "react";

export interface AgentStep {
  id: number;
  event: string;
  tool?: string;
  input?: string;
  output?: string;
  message?: string;
  timestamp: number;
}

export function useAgentStream() {
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const idCounter = useRef(0);

  const start = useCallback((caseId: string) => {
    setSteps([]);
    setIsRunning(true);
    setError(null);
    idCounter.current = 0;

    const eventSource = new EventSource(`/api/chargebacks/${caseId}/resolve`);

    const pushStep = (event: string, data: Record<string, unknown>) => {
      idCounter.current += 1;
      setSteps((prev) => [
        ...prev,
        {
          id: idCounter.current,
          event,
          tool: data.tool as string | undefined,
          input: data.input as string | undefined,
          output: data.output as string | undefined,
          message: data.message as string | undefined,
          timestamp: Date.now(),
        },
      ]);
    };

    eventSource.addEventListener("agent_start", (e) => {
      pushStep("agent_start", JSON.parse(e.data));
    });

    eventSource.addEventListener("tool_start", (e) => {
      pushStep("tool_start", JSON.parse(e.data));
    });

    eventSource.addEventListener("tool_end", (e) => {
      pushStep("tool_end", JSON.parse(e.data));
    });

    eventSource.addEventListener("agent_end", (e) => {
      pushStep("agent_end", JSON.parse(e.data));
      setIsRunning(false);
      eventSource.close();
    });

    eventSource.addEventListener("error", (e) => {
      if (e instanceof MessageEvent) {
        const data = JSON.parse(e.data);
        setError(data.message || "Unknown error");
      } else {
        setError("Connection to agent lost");
      }
      setIsRunning(false);
      eventSource.close();
    });

    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) {
        setIsRunning(false);
      }
    };

    return () => {
      eventSource.close();
      setIsRunning(false);
    };
  }, []);

  const reset = useCallback(() => {
    setSteps([]);
    setIsRunning(false);
    setError(null);
  }, []);

  return { steps, isRunning, error, start, reset };
}
