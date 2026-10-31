import type {
  PreferenceWeights,
  RelaxationSuggestion
} from "../../types/api";

const labels: Record<keyof PreferenceWeights, string> = {
  price: "价格优先",
  duration: "耗时最短",
  comfort: "乘坐舒适",
  schedule: "时间合适"
};

interface PreferencePanelProps {
  weights: PreferenceWeights;
  suggestions: RelaxationSuggestion[];
  onChange: (weights: PreferenceWeights) => void;
}

export function PreferencePanel({
  weights,
  suggestions,
  onChange
}: PreferencePanelProps) {
  function update(key: keyof PreferenceWeights, value: number) {
    const raw = { ...weights, [key]: value };
    const total = Object.values(raw).reduce((sum, item) => sum + item, 0);
    const normalized = Object.fromEntries(
      Object.entries(raw).map(([name, weight]) => [name, weight / total])
    ) as unknown as PreferenceWeights;
    onChange(normalized);
  }

  return (
    <aside className="preference-panel surface-card">
      <div className="section-heading compact">
        <p className="eyebrow">偏好控制台</p>
        <h2>你更在意什么？</h2>
        <p>权重会自动归一化，结果随之重新排序。</p>
      </div>

      <div className="slider-list">
        {(
          Object.keys(labels) as Array<keyof PreferenceWeights>
        ).map((key) => (
          <label className="slider-row" key={key}>
            <span>{labels[key]}</span>
            <strong>{Math.round(weights[key] * 100)}%</strong>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={weights[key]}
              onChange={(event) => update(key, Number(event.target.value))}
            />
          </label>
        ))}
      </div>

      {suggestions.length > 0 && (
        <div className="relaxation-list">
          <p>结果较少，可以尝试放宽：</p>
          {suggestions.map((item) => (
            <div key={`${item.field}-${item.suggested_value}`}>
              <strong>{item.reason}</strong>
              <span>建议值：{item.suggested_value}</span>
            </div>
          ))}
        </div>
      )}

      <div className="framework-note">
        <span>框架预留</span>
        <p>到达时间、车站偏好、行李和换乘风险都可以作为新的评分维度接入。</p>
      </div>
    </aside>
  );
}
