import { useState } from "react";
import { parseTravelRequest } from "../../services/api";
import type { TravelRequest } from "../../types/api";

interface SearchPanelProps {
  request: TravelRequest;
  disabled: boolean;
  onChange: (request: TravelRequest) => void;
  onSearch: () => void;
}

type InputMode = "form" | "assistant";

export function SearchPanel({
  request,
  disabled,
  onChange,
  onSearch
}: SearchPanelProps) {
  const [mode, setMode] = useState<InputMode>("form");
  const [assistantText, setAssistantText] = useState(
    "明天上午从上海去杭州，预算 100 元，想坐高铁，越快越好"
  );
  const [assistantStatus, setAssistantStatus] = useState("");

  function patch(next: Partial<TravelRequest>) {
    onChange({ ...request, ...next });
  }

  async function parseNaturalLanguage() {
    setAssistantStatus("正在理解出行需求…");
    try {
      const result = await parseTravelRequest(assistantText);
      const draft = result.request_draft;
      onChange({
        ...request,
        origin: draft.origin ?? request.origin,
        destination: draft.destination ?? request.destination,
        departure_window:
          draft.departure_window ?? request.departure_window,
        max_price: draft.max_price ?? request.max_price,
        seat_classes: draft.seat_classes ?? request.seat_classes,
        weights: draft.weights ?? request.weights
      });
      const missing = result.missing_fields.length
        ? `还需要补充：${result.missing_fields.join("、")}`
        : "已同步到查询表单，你可以继续调整。";
      setAssistantStatus(missing);
    } catch (error) {
      setAssistantStatus(
        error instanceof Error ? error.message : "自然语言解析失败"
      );
    }
  }

  return (
    <section className="search-card surface-card">
      <div className="mode-switch" role="tablist" aria-label="输入方式">
        <button
          className={mode === "form" ? "active" : ""}
          onClick={() => setMode("form")}
          role="tab"
          aria-selected={mode === "form"}
        >
          精细填写
        </button>
        <button
          className={mode === "assistant" ? "active" : ""}
          onClick={() => setMode("assistant")}
          role="tab"
          aria-selected={mode === "assistant"}
        >
          AI 描述
        </button>
      </div>

      {mode === "assistant" ? (
        <div className="assistant-panel">
          <label htmlFor="assistant-input">用一句话描述你的行程</label>
          <textarea
            id="assistant-input"
            value={assistantText}
            onChange={(event) => setAssistantText(event.target.value)}
            rows={4}
          />
          <div className="assistant-actions">
            <span className="field-hint">{assistantStatus}</span>
            <button
              className="button secondary"
              onClick={parseNaturalLanguage}
              disabled={disabled}
            >
              理解需求
            </button>
          </div>
        </div>
      ) : (
        <div className="form-grid">
          <label>
            <span>出发地</span>
            <input
              value={request.origin}
              onChange={(event) => patch({ origin: event.target.value })}
            />
          </label>
          <label>
            <span>目的地</span>
            <input
              value={request.destination}
              onChange={(event) => patch({ destination: event.target.value })}
            />
          </label>
          <label>
            <span>最早出发</span>
            <input
              type="time"
              value={request.departure_window?.start ?? "08:00"}
              onChange={(event) =>
                patch({
                  departure_window: {
                    start: event.target.value,
                    end: request.departure_window?.end ?? "12:00"
                  }
                })
              }
            />
          </label>
          <label>
            <span>最晚出发</span>
            <input
              type="time"
              value={request.departure_window?.end ?? "12:00"}
              onChange={(event) =>
                patch({
                  departure_window: {
                    start: request.departure_window?.start ?? "08:00",
                    end: event.target.value
                  }
                })
              }
            />
          </label>
          <label>
            <span>预算上限</span>
            <div className="input-with-unit">
              <input
                type="number"
                min="0"
                value={request.max_price ?? ""}
                onChange={(event) =>
                  patch({
                    max_price: event.target.value
                      ? Number(event.target.value)
                      : null
                  })
                }
              />
              <small>元</small>
            </div>
          </label>
          <label>
            <span>最长耗时</span>
            <div className="input-with-unit">
              <input
                type="number"
                min="1"
                value={request.max_duration_minutes ?? ""}
                onChange={(event) =>
                  patch({
                    max_duration_minutes: event.target.value
                      ? Number(event.target.value)
                      : null
                  })
                }
              />
              <small>分钟</small>
            </div>
          </label>
        </div>
      )}

      <div className="search-footer">
        <span>样例数据：上海 → 杭州 · 380 趟直达车次</span>
        <button className="button primary" onClick={onSearch} disabled={disabled}>
          {disabled ? "正在分析…" : "寻找最佳方案"}
        </button>
      </div>
    </section>
  );
}
