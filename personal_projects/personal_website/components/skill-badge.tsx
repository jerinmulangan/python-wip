"use client"

import { motion } from "framer-motion"
import { Badge } from "./ui/badge"

interface SkillBadgeProps {
  name: string
}

export default function SkillBadge({ name }: SkillBadgeProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      whileInView={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.05 }}
    >
      <Badge className="px-3 py-1 text-sm">{name}</Badge>
    </motion.div>
  )
}

