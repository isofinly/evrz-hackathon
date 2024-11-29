import clsx from "clsx";
import { HTMLAttributes, ReactNode } from "react";
import { Icon } from "../../general/icon";
import styles from "./styles.module.css";

interface ListProps extends HTMLAttributes<HTMLUListElement> {
  className?: string;
  children: ReactNode;
}

export const List = ({ className, style, children, ...rest }: ListProps) => {
  return (
    <ul className={clsx(styles.list, className)} {...rest}>
      {children}
    </ul>
  );
};
