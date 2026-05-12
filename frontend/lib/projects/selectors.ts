import type { ProjectFilterState, ProjectItem } from "./types";

export function filterAndSortProjects(
  projects: ProjectItem[],
  filters: Omit<ProjectFilterState, "view">,
): ProjectItem[] {
  const query = filters.query.trim().toLowerCase();

  let next = projects.filter((project) => {
    const matchesQuery =
      !query ||
      project.name.toLowerCase().includes(query) ||
      project.description.toLowerCase().includes(query);
    const matchesPlatform = filters.platform === "all" || project.platform === filters.platform;
    const matchesStatus = filters.status === "all" || project.status === filters.status;

    return matchesQuery && matchesPlatform && matchesStatus;
  });

  next = [...next].sort((a, b) => {
    if (filters.sortBy === "updated") {
      return compareUpdatedAtLabel(a.updatedAtLabel, b.updatedAtLabel);
    }
    if (filters.sortBy === "health-desc") {
      return b.aiHealthScore - a.aiHealthScore;
    }
    if (filters.sortBy === "health-asc") {
      return a.aiHealthScore - b.aiHealthScore;
    }
    return b.commitVelocity - a.commitVelocity;
  });

  return next;
}

function compareUpdatedAtLabel(first: string, second: string): number {
  return parseRelativeLabel(first) - parseRelativeLabel(second);
}

function parseRelativeLabel(label: string): number {
  const normalized = label.toLowerCase().trim();
  if (normalized.endsWith("m ago")) {
    return extractAmount(normalized);
  }
  if (normalized.endsWith("h ago")) {
    return extractAmount(normalized) * 60;
  }
  if (normalized.endsWith("d ago")) {
    return extractAmount(normalized) * 60 * 24;
  }
  return Number.MAX_SAFE_INTEGER;
}

function extractAmount(label: string): number {
  const amount = Number.parseInt(label, 10);
  return Number.isNaN(amount) ? Number.MAX_SAFE_INTEGER : amount;
}

