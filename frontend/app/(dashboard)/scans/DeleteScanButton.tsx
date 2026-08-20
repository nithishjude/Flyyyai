"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/Toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DeleteScanButton({ scanId }: { scanId: string }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();
  const { showToast } = useToast();

  async function handleDelete() {
    if (!confirm("Are you sure you want to delete this scan and all its assets?")) {
      return;
    }

    setIsDeleting(true);
    try {
      const res = await fetch(`${API_BASE}/scans/${scanId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error(`Failed to delete: ${res.status}`);
      }

      showToast("Scan deleted successfully", "success");
      router.refresh();
    } catch (err: any) {
      showToast(err.message || "Failed to delete scan", "error");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <button
      className="btn"
      style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", backgroundColor: "transparent", color: "var(--amber)", border: "1px solid var(--amber)" }}
      onClick={handleDelete}
      disabled={isDeleting}
    >
      {isDeleting ? "Deleting..." : "Delete"}
    </button>
  );
}
