const BadComponent = (props) => {
  const { title, onClick } = props;

  return (
    <div onClick={onClick}>
      <h1>{title}</h1>
      <p>This component has poor typing!</p>
    </div>
  );
};

type LooseProps = any;

const TerribleComponent: React.FC<LooseProps> = ({ content, isActive }) => {
  return (
    <section>
      <div>{content}</div>
      {isActive && <span>Active!</span>}
    </section>
  );
};

export { BadComponent, TerribleComponent };
